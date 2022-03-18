import { Table, Button, Select } from '@mantine/core';
import { useState } from 'react';
import { useQuery } from 'react-query'
import moment from 'moment';
import Loader from '../componentes/loader';


export default function Settings() {
  const [selectedNamespace, changeNamespace] = useState("default");

  const namespaces = useQuery('namespaces', async () =>{
      const req = await fetch(`${import.meta.env.VITE_K8S_API_BASE}/api/v1/namespaces`)
      const data = await req.json()
      return data.items.map((namespace: any) => namespace.metadata.name)
    }
  )

  const deployments = useQuery(['deployments', selectedNamespace], () =>
    fetch(`${import.meta.env.VITE_K8S_API_BASE}/apis/apps/v1/namespaces/${selectedNamespace}/deployments`).then(res =>
      res.json()
    )
  )

  if (deployments.isLoading || namespaces.isLoading) return <Loader />;

  if (deployments.error || namespaces.error) return <p>Error while connecting to Kube API</p>


  const rows = deployments.data?.items?.map((deployment: any) => (
    <tr key={deployment.metadata.uid}>
      <td>{deployment.metadata.name}</td>
      <td>{deployment.status.readyReplicas}/{deployment.status.replicas}</td>
      <td>{deployment.status.updatedReplicas}</td>
      <td>{deployment.status.availableReplicas}</td>
      <td>{moment(deployment.metadata.creationTimestamp).fromNow()}</td>
      <td><Button>Monitor </Button></td>
    </tr>
  ));

  return (
    <>
    <Select
      label="Namespace"
      placeholder="Namespace"
      value={selectedNamespace}
      onChange={(v: string) => changeNamespace(v)}
      data={namespaces?.data}
    />
    <Table>
      <thead>
        <tr>
          <th>Name</th>
          <th>Ready</th>
          <th>Up-to-date</th>
          <th>Available</th>
          <th>Created</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>{rows}</tbody>
    </Table>
    </>
  );
}