import { Table, Button, Select } from '@mantine/core';
import { useState } from 'react';
import { useQuery } from 'react-query'
import moment from 'moment';
import Loader from '../componentes/loader';
import TableSort from '../componentes/table-sort';


export default function Settings() {
  const [selectedNamespace, changeNamespace] = useState("default");

  const namespaces = useQuery('namespaces', async () =>{
      const req = await fetch(`${import.meta.env.VITE_K8S_API_BASE}/api/v1/namespaces`)
      const data = await req.json()
      return data.items.map((namespace: any) => namespace.metadata.name)
    }
  )

  const deployments = useQuery(['deployments', selectedNamespace], async () => {
    const req = await fetch(`${import.meta.env.VITE_K8S_API_BASE}/apis/apps/v1/namespaces/${selectedNamespace}/deployments`)
    const data = await req.json()
    return data.items.map((deployment: any) => (
      {
        id: deployment.metadata.uid,
        name: deployment.metadata.name,
        ready: `${deployment.status.readyReplicas}/${deployment.status.replicas}`,
        up2Date: deployment.status.updatedReplicas,
        available: deployment.status.availableReplicas,
        created: moment(deployment.metadata.creationTimestamp).fromNow(),
        monitored: "true",
      }
    ));
  }
  )

  if (deployments.isLoading || namespaces.isLoading) return <Loader />;

  if (deployments.error || namespaces.error) return <p>Error while connecting to Kube API</p>


  return (
    <div className="flex flex-col">
      <div className='mb-10 self-end'>
        <Select
          className="w-1/4 min-w-fit"
          label="Namespace"
          placeholder="Namespace"
          value={selectedNamespace}
          onChange={(v: string) => changeNamespace(v)}
          data={namespaces?.data}
        />
      </div>
      <div>
        <TableSort data={deployments.data} />
      </div>
    </div>
  );
}