import {Group, Paper, Stack, Text, ThemeIcon} from "@mantine/core";

export function MetadataSmallCard({ icon: Icon, title, value, color, isTruncated }) {
    const pastelMap = {
      blue: { bg: '#F3F0FF', icon: '#A197FF' },
      teal: { bg: '#EBFBEE', icon: '#66D19E' },
      orange: { bg: '#FFF9DB', icon: '#FFD56D' },
    };
    const theme = pastelMap[color] || pastelMap.blue;
    return (
      <Paper radius="18px" p="md" style={{ backgroundColor: theme.bg }}>
        <Group gap="sm" wrap="nowrap">
          <ThemeIcon size={34} radius="50%" style={{ backgroundColor: theme.icon }}><Icon size={18} /></ThemeIcon>
          <Stack gap={0} style={{ flex: 1, overflow: 'hidden' }}>
            <Text fw={900} size="md" c="dark.7" truncate={isTruncated}>{value}</Text>
            <Text size="10px" c="dimmed" fw={700} tt="uppercase">{title}</Text>
          </Stack>
        </Group>
      </Paper>
    );
}
