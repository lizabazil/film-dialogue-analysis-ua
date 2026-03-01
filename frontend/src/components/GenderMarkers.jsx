import {useState} from 'react';
import {
    Paper, Text, Group, Stack, Box, Title, SimpleGrid,
    Badge, ThemeIcon, Button, Center
} from '@mantine/core';
import {
    IconTarget, IconGenderMale, IconGenderFemale,
    IconSparkles, IconChevronDown, IconChevronUp
} from '@tabler/icons-react';

const MarkerRow = ({item, idx, color, maxCount}) => {
    const percentage = (item.count / maxCount) * 100;

    return (
        <Box
            style={{
                position: 'relative',
                borderRadius: '8px',
                overflow: 'hidden',
                backgroundColor: '#f8f9fa',
                height: '36px',
            }}
        >
            <Box
                style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    bottom: 0,
                    width: `${percentage}%`,
                    backgroundColor: color,
                    opacity: 0.12,
                    transition: 'width 1s cubic-bezier(0.2, 0.8, 0.2, 1)',
                }}
            />

            <Box
                style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    bottom: 0,
                    width: '3px',
                    backgroundColor: color,
                    opacity: 0.6,
                }}
            />

            <Group
                justify="apart"
                h="100%"
                px="sm"
                style={{position: 'relative', zIndex: 2}}
                wrap="nowrap"
            >
                <Group gap="xs" style={{flex: 1}}>
                    <Text size="xs" fw={800} c="dimmed" style={{width: '18px', fontVariantNumeric: 'tabular-nums'}}>
                        {idx + 1}
                    </Text>
                    <Text fw={700} size="sm" c="dark.4" truncate>
                        {item.word}
                    </Text>
                </Group>

                <Badge
                    variant="white"
                    color="gray"
                    size="sm"
                    styles={{label: {color: '#495057', fontWeight: 800}}}
                >
                    {item.count}
                </Badge>
            </Group>
        </Box>
    );
};

const MarkerColumn = ({title, markers, color, icon: Icon, maxCount}) => (
    <Stack gap="sm">
        <Group gap="sm" mb={4} px={4}>
            <ThemeIcon
                variant="filled"
                color={color}
                radius="xl"
                size="sm"
            >
                <Icon size={14}/>
            </ThemeIcon>
            <Text fw={900} size="xs" c="dark.3" tt="uppercase" style={{letterSpacing: '1px'}}>
                {title}
            </Text>
        </Group>

        <Stack gap={6}>
            {markers.length > 0 ? (
                markers.map((item, idx) => (
                    <MarkerRow
                        key={`${item.word}-${idx}`}
                        item={item}
                        idx={idx}
                        color={color}
                        maxCount={maxCount}
                    />
                ))
            ) : (
                <Text size="xs" c="dimmed" fs="italic" py="md" ta="center">Дані відсутні</Text>
            )}
        </Stack>
    </Stack>
);

export function GenderMarkers({data}) {
    const [showAll, setShowAll] = useState(false);
    const colors = {man: '#2D4396', woman: '#E64980'};

    const displayLimit = showAll ? 30 : 10;
    const manMarkers = data?.filter(i => i.gender === 'man').slice(0, displayLimit) || [];
    const womanMarkers = data?.filter(i => i.gender === 'woman').slice(0, displayLimit) || [];

    const manMaxCount = manMarkers.length > 0 ? Math.max(...manMarkers.map(i => i.count)) : 1;
    const womanMaxCount = womanMarkers.length > 0 ? Math.max(...womanMarkers.map(i => i.count)) : 1;

    const hasMore = (data?.filter(i => i.gender === 'man').length > 10) ||
        (data?.filter(i => i.gender === 'woman').length > 10);

    return (
        <Paper radius="32px" p="xl" withBorder shadow="sm" bg="white" mb="xl">
            <Stack gap="xl">
                <Group justify="apart">
                    <Stack gap={0}>
                        <Group gap={8}>
                            <Title order={3} fw={900} c="dark.4" style={{letterSpacing: '-0.5px'}}>
                                Лексичні маркери
                            </Title>
                            <ThemeIcon variant="light" color="yellow" radius="xl" size="md">
                                <IconSparkles size={16}/>
                            </ThemeIcon>
                        </Group>
                        <Text size="sm" c="dimmed" fw={500}>Унікальні терміни та їх частота в діалогах</Text>
                    </Stack>
                </Group>

                <SimpleGrid cols={{base: 1, md: 2}} spacing={50}>
                    <MarkerColumn
                        title="Чоловічі репліки"
                        markers={manMarkers}
                        color={colors.man}
                        icon={IconGenderMale}
                        maxCount={manMaxCount}
                    />
                    <MarkerColumn
                        title="Жіночі репліки"
                        markers={womanMarkers}
                        color={colors.woman}
                        icon={IconGenderFemale}
                        maxCount={womanMaxCount}
                    />
                </SimpleGrid>

                {hasMore && (
                    <Center>
                        <Button
                            variant="light"
                            color="gray"
                            size="xs"
                            radius="xl"
                            leftSection={showAll ? <IconChevronUp size={14}/> : <IconChevronDown size={14}/>}
                            onClick={() => setShowAll(!showAll)}
                            fw={800}
                            px="xl"
                        >
                            {showAll ? "Згорнути" : "Показати ще 20 термінів"}
                        </Button>
                    </Center>
                )}

                <Box
                    p="sm"
                    style={{
                        backgroundColor: '#f8f9fa',
                        borderRadius: '16px',
                        border: '1px dashed #dee2e6'
                    }}
                >
                    <Group gap="sm" wrap="nowrap">
                        <ThemeIcon variant="white" radius="xl" size="sm">
                            <IconTarget size={14} color="#868e96"/>
                        </ThemeIcon>
                        <Text size="xs" c="dimmed" fw={600} style={{lineHeight: 1.5}}>
                            <Text component="span" fw={900} c="dark.3">TF-IDF МАРКЕРИ:</Text> Алгоритм відфільтровує
                            спільну лексику та виділяє слова, які є математично найбільш специфічними для кожної статі.
                        </Text> </Group>
                </Box>
            </Stack>
        </Paper>
    );
}