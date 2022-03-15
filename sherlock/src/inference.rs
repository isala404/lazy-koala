use std::{thread, time::Duration, collections::HashMap, env::var};
use serde::{Serialize, Deserialize};
use serde_json::json;
use prometheus::GaugeVec;
use lazy_static::lazy_static;
use prometheus::{opts, register_gauge_vec};
use smartcore::metrics::mean_absolute_error::MeanAbsoluteError;
use crate::query::build_telemetry_matrix;
use ::slice_of_array::prelude::*;


lazy_static! {
    static ref TENSORFLOW_END_POINT: String = var("TENSORFLOW_END_POINT").unwrap_or("http://localhost:8501/v1/models".to_string());
    static ref POOL_DURATION: String = var("POOL_DURATION").unwrap_or("60".to_string());
    static ref ANOMLAY_GAUGE: GaugeVec = register_gauge_vec!(
        opts!(
            "anomaly_score",
            "Reconstruction loss of the autoencoder"
        ),
        &["serviceName", "namespace"]
    )
    .unwrap();
}

#[derive(Debug, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
struct InferenceData {
    model_name: String,
    namespace: String,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ModelResponse {
    pub predictions: Vec<Vec<Vec<Vec<f64>>>>,
}


fn parse_config() -> Result<HashMap<String, InferenceData>, Box<dyn std::error::Error>> {
    let f = std::fs::File::open("config/services.yaml")?;
    let services: HashMap<String, InferenceData> = serde_yaml::from_reader(f)?;
    Ok(services)
}

async fn query_model(service: &str, input: [[[f64; 1]; 9]; 10]) -> Result<f64, Box<dyn std::error::Error>> {
    let endpoint = format!("{}/{}:predict", TENSORFLOW_END_POINT.as_str(), service);

    let query = json!({
        "instances": [input],
    });

    let client = reqwest::Client::new();
    let res = client.post(endpoint)
        .json::<serde_json::Value>(&query)
        .send()
        .await?;

    let predictions = res.json::<ModelResponse>().await?.predictions.into_iter().flatten().flatten().flatten().collect::<Vec<f64>>();

    let mse: f64 = MeanAbsoluteError{}.get_score(&input.flat().flat().to_vec(), &predictions);
    
    Ok(mse)
}

async fn calculate_anomaly_score(service: &str, args: &InferenceData) -> Result<(), Box<dyn std::error::Error>> {
    println!("Calculate anomaly score for {} using {}", service, &args.model_name);
    let input = build_telemetry_matrix(&service).await?;
    let score = query_model(&args.model_name, input).await?;
    ANOMLAY_GAUGE.with_label_values(&[service, &args.namespace]).set(score);
    println!("Anomaly score for {}: {}", service, score);
    Ok(())
}

pub async fn poll_anomaly_scores() {
    let delay = POOL_DURATION.as_str().parse::<u64>().unwrap();

    loop {
        let services = parse_config().unwrap_or_default();

        for (service, args) in services.iter() {
            if let Err(err) = calculate_anomaly_score(service, args).await {
                eprintln!("Error while calculating anomaly score: {}", err);
                ANOMLAY_GAUGE.with_label_values(&[service, &args.namespace]).set(-1.0)
            }
        }
        thread::sleep(Duration::from_secs(delay));
    }
}
