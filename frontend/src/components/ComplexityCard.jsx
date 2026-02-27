import { Paper, Text, Group, ThemeIcon, Stack, Grid } from '@mantine/core';
import { IconMan, IconWoman } from '@tabler/icons-react';


function ComplexityCard({ label, value, color, icon: Icon }) {
  return (
    <Paper
      p="xl"
      radius="28px"
      bg="white"
      style={{
        boxShadow: '0 10px 30px rgba(0, 0, 0, 0.04)',
        border: '1px solid #f1f3f5'
      }}
    >
      <Group wrap="nowrap">
        <ThemeIcon
          size={54}
          radius="xl"
          variant="light"
          color={color}
        >
          <Icon size={28} />
        </ThemeIcon>

        <Stack gap={2}>
          <Text size="xs" c="dimmed" fw={700} tt="uppercase" lts="1px">
            {label}
          </Text>
          <Group align="flex-baseline" gap={4}>
            <Text size="28px" fw={900} c="dark.5">
              {(value || 0).toFixed(1)}
            </Text>
            <Text size="sm" c="dimmed" fw={500}>слів/репліка</Text>
          </Group>
        </Stack>
      </Group>
    </Paper>
  );
}


export function SpeechComplexity({ manMlu, womanMlu }) {
  return (
    <Grid gutter="md">
      <Grid.Col span={{ base: 12, md: 6 }}>
        <ComplexityCard
          label="Красномовність (Чоловіки)"
          value={manMlu}
          color="indigo"
          icon={IconMan}
        />
      </Grid.Col>
      <Grid.Col span={{ base: 12, md: 6 }}>
        <ComplexityCard
          label="Красномовність (Жінки)"
          value={womanMlu}
          color="pink"
          icon={IconWoman}
        />
      </Grid.Col>
    </Grid>
  );
}
