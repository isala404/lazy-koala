import React, {useEffect, useState} from "react";
import { ForceGraph2D, } from 'react-force-graph';
import { useQuery } from 'react-query'

const normlize = (val: number) => {
    const min = 7000000;
    const max = 34666972

    return (val - min) / (max - min); 
}

function getColor(value: any){
    //value from 0 to 1
    var hue=((1-value)*120).toString(10);
    return ["hsl(",hue,",100%,50%)"].join("");
}

function getRandomRgb() {
    var num = Math.round(0xffffff * Math.random());
    var r = num >> 16;
    var g = num >> 8 & 255;
    var b = num & 255;
    return 'rgb(' + r + ', ' + g + ', ' + b + ')';
  }

export default function Dashboard() {
    const [data, setData] = useState<any>({"nodes": [], "links": []})

    const anomaly_score = useQuery('anomaly_score', async () => {
        const req = await fetch(`${import.meta.env.VITE_PROM_API_BASE}/api/v1/query?query=anomaly_score`)
        const data = await req.json()
        const scores: any = {}
        
        data.data.result.map((r: any) => {
            scores[r.metric.serviceName] = parseFloat(r.value[1])
            return r
        })
        return scores
    });

    const services = useQuery(['services', anomaly_score], async () => {
        const req = await fetch(`${import.meta.env.VITE_K8S_API_BASE}/apis/lazykoala.isala.me/v1alpha1/inspectors`)
        const data = await req.json()

        const serviceData: any = {}
        
        data.items.map((item: any) => {
            serviceData[item.metadata.name] = {
                "id": item.metadata.name,
                "group": item.spec.namespace,
                "anomalyScore": normlize(anomaly_score.data[item.metadata.name] || -1)
            }
            return item
        })

        return serviceData
    }, {enabled: !!anomaly_score.data});

    const request_exchanges = useQuery('request_exchanges', async () => {
        const req = await fetch(`${import.meta.env.VITE_PROM_API_BASE}/api/v1/query?query=rate%28request_exchanges_total%5B5m%5D%29`)
        let data = await req.json()

        data = data.data.result.map((r: any) => ({
            "source": r.metric.origin,
            "target": r.metric.destination,
            "value": parseFloat(r.value[1])
        }))

        return data.filter((d: any) => d["source"] in services.data && d["target"] in services.data)
    }, {enabled: !!services.data});

    useEffect(() => {
        if(request_exchanges.data){
            setData({"nodes": Object.values(services.data), "links": request_exchanges.data});
            console.log({"nodes": Object.values(services.data), "links": request_exchanges.data})
        }        
        // fetch("https://raw.githubusercontent.com/vasturiano/react-force-graph/master/example/datasets/miserables.json").then(res => res.json()).then(data => {setData(data)})
    }, [request_exchanges.isFetched])

    return(
        <>
            <ForceGraph2D
                width={950}
                height={800}
                // onEngineStop={() => fgRef.current.zoomToFit(400)}
                graphData={data}
                nodeLabel="id"
                nodeAutoColorBy="anomalyScore"
                nodeRelSize={3}
                // minZoom={10}
                nodeCanvasObject={(node: any, ctx: CanvasRenderingContext2D, globalScale) => {
                    const label = `${node.id} (${Math.round(node.anomalyScore * 100) / 100})`;
                    const fontSize = 14/globalScale;
                    ctx.font = `${fontSize}px Sans-Serif`;
                    const textWidth = ctx.measureText(label).width;
                    const bckgDimensions = [textWidth, fontSize].map(n => n + fontSize * 2.2); // some padding
        
                    ctx.fillStyle = getColor(node.anomalyScore);
                    ctx.fillRect(node.x - bckgDimensions[0] / 2, node.y - bckgDimensions[1] / 2, bckgDimensions[0], bckgDimensions[1]);
                    // ctx.arc(node.x, node.y, 1, 0, 2 * Math.PI)
                    // ctx.stroke()
        
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
                    ctx.fillText(label, node.x, node.y);
                    node.color = getRandomRgb()
                    // console.log(node.color)
                    node.__bckgDimensions = bckgDimensions; // to re-use in nodePointerAreaPaint
                  }}
                linkDirectionalParticles="value"
                linkAutoColorBy="source"
                linkDirectionalParticleSpeed={(d: any) => d.value * 0.0005}
            />,
        </>
    );
}
