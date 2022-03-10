use hyper::{
    header::CONTENT_TYPE,
    service::{make_service_fn, service_fn},
    Body, Request, Response, Server,
};
use prometheus::{Encoder, Gauge, TextEncoder};
use std::{env::var, thread, time::Duration};
use lazy_static::lazy_static;
use prometheus::{labels, opts, register_gauge};
use std::collections::HashMap;

lazy_static! {
    static ref SERVICE_NAME: String = var("SERVICE_NAME").unwrap();
    static ref NAMESPACE: String = var("NAMESPACE").unwrap();
    static ref END_POINT: String = var("END_POINT").unwrap();
    static ref POOL_DURATION: String = var("POOL_DURATION").unwrap();
    static ref ANOMLAY_GAUGE: Gauge = register_gauge!(opts!(
        "anomaly_score",
        "Reconstruction loss of the autoencoder",
        labels! {"serviceName" => SERVICE_NAME.as_str(), "namespace" => NAMESPACE.as_str()}
    ))
    .unwrap();
}

async fn serve_req(_req: Request<Body>) -> Result<Response<Body>, hyper::Error> {
    let encoder = TextEncoder::new();
   
    let metric_families = prometheus::gather();
    let mut buffer = vec![];
    encoder.encode(&metric_families, &mut buffer).unwrap();

    let response = Response::builder()
        .status(200)
        .header(CONTENT_TYPE, encoder.format_type())
        .body(Body::from(buffer))
        .unwrap();

    Ok(response)
}


fn query_model() ->Result<f64, Box<dyn std::error::Error>> {
    let resp = reqwest::blocking::get(END_POINT.as_str())?
                .json::<HashMap<String, f64>>()?;
    Ok(resp["predictions"])
}

fn poll_anomaly_scores(delay: u64) {

    loop {

        if let Ok(value) = query_model(){
            ANOMLAY_GAUGE.set(value);
        }

        thread::sleep(Duration::from_secs(delay));
    }
}

#[tokio::main]
async fn main() {

    thread::spawn(|| poll_anomaly_scores(POOL_DURATION.as_str().parse::<u64>().unwrap()));

    ANOMLAY_GAUGE.set(0.0);
    
    let addr = ([0, 0, 0, 0], 9898).into();
    println!("Listening on http://{}", addr);

    let serve_future = Server::bind(&addr).serve(make_service_fn(|_| async {
        Ok::<_, hyper::Error>(service_fn(serve_req))
    }));

    if let Err(err) = serve_future.await {
        eprintln!("server error: {}", err);
    }
}