import {Group, Paper, Progress, Stack, Text, ThemeIcon, Center} from "@mantine/core";


export function KeywordBarChart({title, keywords, baseColor, icon: Icon}) {
    const slicedKeywords = keywords?.slice(0, 20) || [];
    const maxCount = slicedKeywords.length > 0 ? Math.max(...slicedKeywords.map(k => k.count)) : 1;
    const totalItems = slicedKeywords.length;

    return (
        <Paper radius="32px" p="lg" withBorder shadow="sm" bg="white" h="100%" style={{border: '1px solid #f1f3f5'}}>
            <Stack gap="md">
                <Group gap="xs" mb="xs">
                    <ThemeIcon variant="light" color="gray" radius="md" size="md">
                        <Icon size={16}/>
                    </ThemeIcon>

                    <Text fw={800} size="md" c="dark.4" style={{letterSpacing: '0.5px', textTransform: 'uppercase'}}>
                        {title}
                    </Text>
                </Group>

                <Stack gap="sm">
                    {slicedKeywords.map((item, index) => {
                        const lightenIntensity = (index / Math.max(1, totalItems - 1)) * 50;
                        const rowColor = `color-mix(in srgb, ${baseColor}, white ${lightenIntensity}%)`;

                        return (
                            <Stack key={index} gap={4}>
                                <Group justify="space-between" wrap="nowrap">

                                    <Text size="sm" fw={700} c="dark.6"
                                          style={{whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis'}}>
                                        {item.word}
                                    </Text>

                                    <Text size="sm" fw={700} c="dimmed">
                                        {item.count}
                                    </Text>

                                </Group>
                                <Progress
                                    value={(item.count / maxCount) * 100}
                                    color={rowColor}
                                    size="md"
                                    radius="xl"
                                    styles={{section: {transition: 'width 1s ease'}}}
                                />
                            </Stack>
                        );
                    })}
                    {slicedKeywords.length === 0 && (
                        <Center h={100}>
                            <Text size="sm" c="dimmed">Дані відсутні</Text>
                        </Center>
                    )}
                </Stack>
            </Stack>
        </Paper>
    );
}