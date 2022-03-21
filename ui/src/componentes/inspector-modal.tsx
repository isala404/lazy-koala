import { Button, Text } from '@mantine/core';
import { useModals } from '@mantine/modals';
import { useMutation } from 'react-query';
import { useQuery, useQueryClient } from 'react-query'

interface UnmonitorProps {
    namespace: string;
    service: string;
    deployment: string;
    name: string;
}
  

export function Unmonitor({service, deployment, name, namespace}: UnmonitorProps) {
    const queryClient = useQueryClient()

    const mutation = useMutation(async () => {
        const req = await fetch(
            `${import.meta.env.VITE_K8S_API_BASE}/apis/lazykoala.isala.me/v1alpha1/namespaces/${namespace}/inspectors/${name}`,
            {method: "DELETE"}
        )
        req
      }, {
          onSuccess: () => {
              queryClient.invalidateQueries("inspectors")
          }
      });


  const modals = useModals();

  const openConfirmModal = () => modals.openConfirmModal({
    title: 'Please confirm your action',
    children: (
      <Text size="sm">
        Deleting <code>{name}</code> resource will result in <code>{deployment}</code> deployment and <code>{service}</code> and ClusterIP being untracked and exluded from service graph
      </Text>
    ),
    labels: { confirm: 'Confirm', cancel: 'Cancel' },
    onCancel: () => console.log('Cancel'),
    onConfirm: () => mutation.mutate(),
  });

  return <Button color="red" onClick={openConfirmModal}>Unmonitor</Button>
}