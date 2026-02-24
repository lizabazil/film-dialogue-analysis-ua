import {Stack, Text} from "@mantine/core";

export function LegendDetail({ label, value, color }) {
    return (
        <Stack gap={0} align="center">
            <Text size="xs" c="dimmed" fw={700} tt="uppercase">{label}</Text>
            <Text fw={800} c={color}>{value}</Text>
        </Stack>
    );
}