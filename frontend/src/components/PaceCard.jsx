import {Group, Paper, Stack, Text, ThemeIcon} from "@mantine/core";

export const PaceCard = ({title, value, icon: Icon, color, subtext}) => (
    <Paper radius="32px" p="lg" withBorder shadow="sm" bg="white" style={{flex: 1}}>
        <Group justify="apart" mb="xs">
            <ThemeIcon size="xl" radius="md" variant="light" color={color}>
                <Icon size={24}/>
            </ThemeIcon>
            <Text fw={800} size="xl" c="dark.4">{value}</Text>
        </Group>
        <Stack gap={0}>
            <Text size="sm" fw={700} c="dark.3">{title}</Text>
            <Text size="xs" c="dimmed">{subtext}</Text>
        </Stack>
    </Paper>
);
