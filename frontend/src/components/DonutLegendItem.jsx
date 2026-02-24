import {Box, Group, Stack, Text} from "@mantine/core";

export function DonutLegendItem({ color, label, value, percent }) {
  return (
    <Group justify="space-between" wrap="nowrap" gap="xl">
      <Group gap="xs">
        <Box w={8} h={8} style={{ borderRadius: '50%', backgroundColor: color }} />
        <Text size="sm" fw={700} c="dark.3">{label}</Text>
      </Group>
      <Stack gap={0} align="flex-end">
        <Text size="sm" fw={800}>{percent}%</Text>
        <Text size="15px" c="dimmed">{value} шт.</Text>
      </Stack>
    </Group>
  );
}
