import { Box, Button, Group, Modal, Select, Text, TextInput } from '@mantine/core';
import { useForm } from '@mantine/form';
import { useModals } from '@mantine/modals';
import { useState } from 'react';
import { useMutation } from 'react-query';
import { useQuery, useQueryClient } from 'react-query'
import Loader from '../components/loader';
import { useNotifications } from '@mantine/notifications';

interface MonitorProps {
    deployment: string;
    namespace: string;
}

const inspectorSample = {
    apiVersion: 'lazykoala.isala.me/v1alpha1',
    kind: 'Inspector',
    namespace: 'lazy-koala',
    metadata: {
        name: 'flowtest-sample',
    },
    spec: {
        deploymentRef: "",
        serviceRef: "",
        modelName: "",
        namespace: ""
    },
};



export default function Monitor({ deployment, namespace }: MonitorProps) {
    const [opened, setOpened] = useState(false);
    const notifications = useNotifications();

    const form = useForm({
        initialValues: {
            resourceName: deployment,
            modelName: '',
            endpoint: '',
        },
    });

    const queryClient = useQueryClient()

    const services = useQuery('services', async () => {
        const req = await fetch(`${import.meta.env.VITE_K8S_API_BASE}/api/v1/namespaces/${namespace}/services`)
        const data = await req.json()
        return data.items.map((namespace: any) => namespace.metadata.name)
    });

    const mutation = useMutation('deleteInspector', async (value: any) => {
        let object = JSON.parse(JSON.stringify(inspectorSample))

        object.metadata.name = value.resourceName
        object.spec.deploymentRef = deployment
        object.spec.serviceRef = value.endpoint
        object.spec.modelName = value.modelName
        object.spec.namespace = namespace


        const req = await fetch(
            `${import.meta.env.VITE_K8S_API_BASE}/apis/lazykoala.isala.me/v1alpha1/namespaces/${namespace}/inspectors/${name}`, {
            method: "POST",
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(object),
        })

        const data = await req.json()

        if (!req.ok) {
            notifications.showNotification({
                title: "Error while deploying Inspector",
                message: data.message,
                color: 'red'
            })
        } else {
            notifications.showNotification({
                title: "New Inspector deployed",
                message: `${value.modelName} was deployed to monitor ${deployment}`,
                color: 'green'
            })
            queryClient.invalidateQueries("inspectors")
            setOpened(false);
        }

        return data
    });

    if (services.isLoading) return <Loader />


    return (
        <>
            <Modal
                title={'Create a new Inspector Resource'}
                closeOnEscape={false}
                onClose={() => setOpened(false)}
                opened={opened}
            >
                <form onSubmit={form.onSubmit((values) => mutation.mutate(values))}>
                    <TextInput
                        required
                        label="Resource name"
                        placeholder="service-1"
                        description="ID used by the kubernetes to identify each resource"
                        {...form.getInputProps('resourceName')}
                    />
                    <TextInput
                        required
                        label="Model name"
                        placeholder="autoeconder-base-v3"
                        description="Model that will be used to calculate anomaly score"
                        {...form.getInputProps('modelName')}
                    />
                    <Select
                        label="Service DNS"
                        placeholder="service-1-cluster-api"
                        data={services?.data}
                        description="Ingress endpoint for the deployment"
                        {...form.getInputProps('endpoint')}
                    />
                    <Group position="right" mt="md">
                        <Button color="teal" type="submit">Monitor</Button>
                    </Group>
                </form>
            </Modal>

            <Button color="teal" className="w-28" onClick={() => setOpened(!opened)}>Monitor</Button>
        </>
    )
}