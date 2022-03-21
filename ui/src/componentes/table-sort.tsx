import React, { useState, useEffect } from 'react';
import {
  createStyles,
  Table,
  ScrollArea,
  UnstyledButton,
  Group,
  Text,
  Center,
  TextInput,
  Button
} from '@mantine/core';
import { Selector, ChevronDown, ChevronUp, Search } from 'tabler-icons-react';
import {Unmonitor, Monitor} from "../componentes/inspector-modal"

const useStyles = createStyles((theme) => ({
  th: {
    padding: '0 !important',
  },

  control: {
    width: '100%',
    padding: `${theme.spacing.xs}px ${theme.spacing.md}px`,

    // '&:hover': {
    //   backgroundColor: theme.colorScheme === 'dark' ? theme.colors.dark[6] : theme.colors.gray[0],
    // },
  },

  icon: {
    width: 21,
    height: 21,
    borderRadius: 21,
  },
}));

interface RowData {
  id: string;
  name: string;
  ready: string;
  created: string;
  modelName: string;
  serviceRef: string;
  status: string;
  monitored: string;
  inspectorName: string;
  namespace: string;
}

interface TableSortProps {
  data: RowData[];
}

interface ThProps {
  children: React.ReactNode;
  reversed: boolean;
  sorted: boolean;
  width?: string;
  onSort(): void;
}

function Th({ children, reversed, sorted, onSort, width="inharit" }: ThProps) {
  const { classes } = useStyles();
  const Icon = sorted ? (reversed ? ChevronUp : ChevronDown) : Selector;
  return (
    <th className={classes.th} style={{width }}>
      <UnstyledButton onClick={onSort} className={classes.control}>
        <Group position="apart" noWrap>
          <Text weight={500} size="sm" className="w-max">
            {children}
          </Text>
          <Center className={classes.icon}>
            <Icon size={14} />
          </Center>
        </Group>
      </UnstyledButton>
    </th>
  );
}

function filterData(data: RowData[], search: string) {
  const keys = Object.keys(data[0]);
  const query = search.toLowerCase().trim();
  return data.filter((item) => keys.some((key) => String(item[key]).toLowerCase().includes(query)));
}

function sortData(
  data: RowData[],
  payload: { sortBy: keyof RowData; reversed: boolean; search: string }
) {
  if (!payload.sortBy) {
    return filterData(data, payload.search);
  }

  return filterData(
    [...data].sort((a, b) => {
      if (payload.reversed) {
        return b[payload.sortBy].localeCompare(a[payload.sortBy]);
      }

      return a[payload.sortBy].localeCompare(b[payload.sortBy]);
    }),
    payload.search
  );
}

export default function TableSort({ data }: TableSortProps) {
  const [search, setSearch] = useState('');
  const [sortedData, setSortedData] = useState(data || []);
  const [sortBy, setSortBy] = useState<keyof RowData>();
  const [reverseSortDirection, setReverseSortDirection] = useState(false);

  useEffect(() => {
    setSortedData(data || []);
  }, [data]);

  const setSorting = (field: keyof RowData) => {
    const reversed = field === sortBy ? !reverseSortDirection : false;
    setReverseSortDirection(reversed);
    setSortBy(field);
    setSortedData(sortData(data, { sortBy: field, reversed, search }));
  };

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { value } = event.currentTarget;
    setSearch(value);
    setSortedData(sortData(data, { sortBy, reversed: reverseSortDirection, search: value }));
  };

  const rows = sortedData.map((row) => (
    <tr key={row.id}>
      <td>{row.name}</td>
      <td>{row.ready}</td>
      <td>{row.created}</td>
      <td>{row.modelName}</td>
      <td>{row.serviceRef}</td>
      <td>{row.status}</td>
      <td>
        {
          row.monitored == "false" ?
            <Monitor name={row.inspectorName} service={row.serviceRef} deployment={row.name} namespace={row.namespace}/>
          :
            <Unmonitor name={row.inspectorName} service={row.serviceRef} deployment={row.name} namespace={row.namespace}/>
        }
      </td>
    </tr>
  ));

  return (
    <ScrollArea>
      <TextInput
        placeholder="Search by any field"
        mb="md"
        icon={<Search size={14} />}
        value={search}
        onChange={handleSearchChange}
      />
      <Table
        // highlightOnHover
        horizontalSpacing="md"
        verticalSpacing="xs"
        sx={{ tableLayout: 'fixed', minWidth: 850 }}
      >
        <thead>
          <tr>
            <Th
              sorted={sortBy === 'name'}
              reversed={reverseSortDirection}
              onSort={() => setSorting('name')}
              width="20%"
            >
              Name
            </Th>
            <Th
              sorted={sortBy === 'ready'}
              reversed={reverseSortDirection}
              onSort={() => setSorting('ready')}
            >
              Ready
            </Th>
            <Th
              sorted={sortBy === 'created'}
              reversed={reverseSortDirection}
              onSort={() => setSorting('created')}
              width="12%"
            >
              Created
            </Th>
            <Th
              sorted={sortBy === 'modelName'}
              reversed={reverseSortDirection}
              onSort={() => setSorting('modelName')}
              width="17%"
            >
              Model Name
            </Th>
            <Th
              sorted={sortBy === 'serviceRef'}
              reversed={reverseSortDirection}
              onSort={() => setSorting('serviceRef')}
              width="17%"
            >
              Service Ref
            </Th>
            <Th
              sorted={sortBy === 'status'}
              reversed={reverseSortDirection}
              onSort={() => setSorting('status')}
            >
              Status
            </Th>
            <Th
              sorted={sortBy === 'monitored'}
              reversed={reverseSortDirection}
              onSort={() => setSorting('monitored')}
              width="15%"
            >
              Action
            </Th>
          </tr>
        </thead>
        <tbody>
          {rows.length > 0 ? (
            rows
          ) : (
            <tr>
              <td colSpan={6}>
                <Text weight={500} align="center">
                  Nothing found
                </Text>
              </td>
            </tr>
          )}
        </tbody>
      </Table>
    </ScrollArea>
  );
}