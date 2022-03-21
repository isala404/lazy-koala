import { Button, Text} from '@mantine/core';
import { useModals } from '@mantine/modals';
import { useMutation } from 'react-query';
import { useQueryClient } from 'react-query'
import { useNotifications } from '@mantine/notifications';

interface UnmonitorProps {
  namespace: string;
  service: string;
  deployment: string;
  name: string;
}

export default function Unmonitor({ service, deployment, name, namespace }: UnmonitorProps) {
  const queryClient = useQueryClient()
  const notifications = useNotifications();

  const mutation = useMutation('deleteInspector', async () => {
    const req = await fetch(
      `${import.meta.env.VITE_K8S_API_BASE}/apis/lazykoala.isala.me/v1alpha1/namespaces/${namespace}/inspectors/${name}`,
      { method: "DELETE" }
    )
    req
  }, {
    onSuccess: () => {
      queryClient.invalidateQueries("inspectors")
      notifications.showNotification({
        title: "Inspector Deleted",
        message: `${deployment} was excluded from the lazy-koala`,
        color: 'yellow'
      })
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
    onConfirm: () => mutation.mutate(),
  });

  return <Button color="red" className="w-28" onClick={openConfirmModal}>Unmonitor</Button>
}