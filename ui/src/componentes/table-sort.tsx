import React, { useState } from 'react';
import {
  createStyles,
  Table,
  ScrollArea,
  UnstyledButton,
  Group,
  Text,
  Center,
  TextInput,
} from '@mantine/core';
import { Selector, ChevronDown, ChevronUp, Search } from 'tabler-icons-react';

const useStyles = createStyles((theme) => ({
  th: {
    padding: '0 !important',
  },

  control: {
    width: '100%',
    padding: `${theme.spacing.xs}px ${theme.spacing.md}px`,

    '&:hover': {
      backgroundColor: theme.colorScheme === 'dark' ? theme.colors.dark[6] : theme.colors.gray[0],
    },
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
  up2Date: string;
  available: string;
  created: string;
  monitored: string;
}

interface TableSortProps {
  data: RowData[];
}

interface ThProps {
  children: React.ReactNode;
  reversed: boolean;
  sorted: boolean;
  first?: boolean;
  onSort(): void;
}

function Th({ children, reversed, sorted, onSort, first=false }: ThProps) {
  const { classes } = useStyles();
  const Icon = sorted ? (reversed ? ChevronUp : ChevronDown) : Selector;
  return (
    <th className={classes.th} style={{width: first ? "25%": "inharit" }}>
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
      <td>{row.up2Date}</td>
      <td>{row.available}</td>
      <td>{row.created}</td>
      <td>{row.monitored}</td>
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
        highlightOnHover
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
              first
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
              sorted={sortBy === 'up2Date'}
              reversed={reverseSortDirection}
              onSort={() => setSorting('up2Date')}
            >
              Up-to-date
            </Th>
            <Th
              sorted={sortBy === 'available'}
              reversed={reverseSortDirection}
              onSort={() => setSorting('available')}
            >
              Available
            </Th>
            <Th
              sorted={sortBy === 'created'}
              reversed={reverseSortDirection}
              onSort={() => setSorting('created')}
            >
              Created
            </Th>
            <Th
              sorted={sortBy === 'monitored'}
              reversed={reverseSortDirection}
              onSort={() => setSorting('monitored')}
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