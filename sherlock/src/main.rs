use hyper::{
    header::CONTENT_TYPE,
    service::{make_service_fn, service_fn},
    Body, Request, Response, Server,
};
use prometheus::{Encoder, GaugeVec, TextEncoder};
use std::{env::var, thread, time::Duration};
use lazy_static::lazy_static;
use prometheus::{opts, register_gauge_vec};
use std::collections::HashMap;
use serde_yaml; 

lazy_static! {
    static ref END_POINT: String = var("END_POINT").unwrap();
    static ref POOL_DURATION: String = var("POOL_DURATION").unwrap();
    static ref ANOMLAY_GAUGE: GaugeVec = register_gauge_vec!(
        opts!(
            "anomaly_score",
            "Reconstruction loss of the autoencoder"
        ),
        &["serviceName"]
    )
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


fn query_model(service: &String) ->Result<f64, Box<dyn std::error::Error>> {
    println!("Querying {} model", service);
    let endpoint = format!("{}/{}:predict", END_POINT.as_str(), service);
    let resp = reqwest::blocking::get(endpoint)?.json::<HashMap<String, f64>>()?;
    Ok(resp["predictions"])
}

fn poll_anomaly_scores(delay: u64) {
    loop {
        match read_config() {
            Ok(services) => {
                for service in services.iter(){
                    match query_model(service) {
                        Ok(score) => ANOMLAY_GAUGE.with_label_values(&[service]).set(score),
                        Err(e) => eprintln!("Error while querying model: {}", e),
                    }
                }
            },
            Err(e) => eprintln!("Error while parsing config: {}", e),
        };
        thread::sleep(Duration::from_secs(delay));
    }
}

fn read_config() -> Result<Vec<String>, Box<dyn std::error::Error>> {
    let f = std::fs::File::open("config/config.yaml")?;
    let services: Vec<String> = serde_yaml::from_reader(f)?;
    Ok(services)
}

#[tokio::main]
async fn main() {
    
    thread::spawn(|| poll_anomaly_scores(POOL_DURATION.as_str().parse::<u64>().unwrap()));

    let addr = ([0, 0, 0, 0], 9898).into();
    println!("Listening on http://{}", addr);

    let serve_future = Server::bind(&addr).serve(make_service_fn(|_| async {
        Ok::<_, hyper::Error>(service_fn(serve_req))
    }));

    if let Err(err) = serve_future.await {
        eprintln!("server error: {}", err);
    }
}