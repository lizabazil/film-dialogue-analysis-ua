import {useRef, useState} from "react";
import {Badge, Box, Divider, Group, Paper, Stack, Text} from "@mantine/core";


export const PaceAreaChart = ({graph}) => {
    const [hoveredPoint, setHoveredPoint] = useState(null);
    const svgRef = useRef(null);

    if (!graph || graph.length < 2) return null;

    const height = 150;
    const width = 1000;
    const maxWords = Math.max(...graph.map(p => p.total_local_words), 1);

    const replicaLabels = {
        reactive: 'Реакція',
        standard: 'Звичайна',
        extended: 'Розгорнута',
        monologue: 'Монолог'
    };

    const pauseLabels = {
        small: 'Коротка',
        normal_pause: 'Звичайна',
        hesitation: 'Заминка',
        long_pause: 'Довга'
    };

    const colors = {
        reactive: '#E3F2FD',
        standard: '#F3E5F5',
        extended: '#E8F5E9',
        monologue: '#FFF3E0',
        pause_small: '#F5F5F5',
        pause_normal: '#E1F5FE',
        pause_hesitation: '#FFF9C4',
        pause_long: '#FFEBEE',
        text: '#4A4A4A',
        label: '#8E8E8E'
    };

    const getTooltipPosition = () => {
        if (!hoveredPoint) return {};

        const percentage = (hoveredPoint.index / (graph.length - 1)) * 100;
        if (percentage < 15) return {left: '5px', transform: 'translate(0, -100%)'};
        if (percentage > 85) return {right: '5px', transform: 'translate(0, -100%)'};
        return {
            left: `${percentage}%`,
            transform: 'translate(-50%, -100%)'
        };
    };

    const formatTime = (ms) => {
        if (!ms || ms < 0) return "0:00:00";
        const totalSeconds = Math.floor(ms / 1000);
        const hours = Math.floor(totalSeconds / 3600);
        const minutes = Math.floor((totalSeconds % 3600) / 60);
        const seconds = totalSeconds % 60;
        const h = hours.toString();
        const m = minutes.toString().padStart(2, '0');
        const s = seconds.toString().padStart(2, '0');
        return `${h}:${m}:${s}`;
    };

    const points = graph.map((p, i) => ({
        x: (i / (graph.length - 1)) * width,
        y: height - (p.total_local_words / maxWords) * height,
        data: p
    }));

    const linePath = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ');
    const areaPath = `${linePath} L ${width} ${height} L 0 ${height} Z`;

    const handleMouseMove = (e) => {
        if (!svgRef.current) return;
        const rect = svgRef.current.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const relativeX = (x / rect.width) * width;
        const index = Math.round((relativeX / width) * (graph.length - 1));
        if (index >= 0 && index < points.length) {
            setHoveredPoint({...points[index], index});
        }
    };

    const gridLines = [0, 0.25, 0.5, 0.75, 1].map((pos, i) => {
        const y = height - pos * height;
        return (
            <line
                key={i}
                x1="0"
                y1={y}
                x2={width}
                y2={y}
                stroke="#e9ecef"
                strokeWidth="1"
                strokeDasharray="4 4"
            />
        );
    });

    return (
        <Box mt="md" style={{position: 'relative'}}>
            {hoveredPoint && (
                <Paper
                    shadow="sm"
                    p="sm"
                    withBorder
                    radius="20px"
                    style={{
                        position: 'absolute',
                        zIndex: 10,
                        pointerEvents: 'none',
                        top: -15,
                        backgroundColor: 'rgba(255, 255, 255, 0.96)',
                        backdropFilter: 'blur(10px)',
                        border: '1px solid #F1F3F5',
                        minWidth: '200px',
                        ...getTooltipPosition()
                    }}
                >
                    <Stack gap={8}>
                        <Group justify="apart" wrap="nowrap">
                            <Text fw={700} size="xs" style={{color: colors.text, letterSpacing: '0.5px'}}>
                                {formatTime(hoveredPoint.data.timestamps_total_ms)}
                            </Text>
                            {hoveredPoint.data.dominant_replica_type && (
                                <Badge
                                    size="xs"
                                    variant="filled"
                                    styles={{
                                        root: {
                                            backgroundColor: colors[hoveredPoint.data.dominant_replica_type],
                                            color: '#555',
                                            fontWeight: 700,
                                            border: 'none'
                                        }
                                    }}
                                >
                                    {replicaLabels[hoveredPoint.data.dominant_replica_type]}
                                </Badge>
                            )}
                        </Group>

                        <Divider variant="dashed" color="#F1F3F5"/>

                        <Stack gap={4}>
                            <Group justify="apart">
                                <Text size="10px" fw={700} c="dimmed">СЛІВ У ВІКНІ</Text>
                                <Text size="xs" fw={700}
                                      style={{color: colors.text}}>{hoveredPoint.data.total_local_words}</Text>
                            </Group>
                            <Group justify="apart">
                                <Text size="10px" fw={700} c="dimmed">ТИША</Text>
                                <Text size="xs" fw={700}
                                      style={{color: colors.text}}>{Math.round(hoveredPoint.data.silence_percentage)}%</Text>
                            </Group>
                        </Stack>

                        {/* pauses info (displaying only if such data exists) */}
                        {hoveredPoint.data.dominant_pause_type && (
                            <>
                                <Divider variant="dashed" color="#F1F3F5"/>
                                <Group justify="apart">
                                    <Text size="10px" fw={700} c="dimmed">ТИП ПАУЗ</Text>
                                    <Badge
                                        size="xs"
                                        variant="dot"
                                        styles={{
                                            root: {
                                                backgroundColor: colors[`pause_${hoveredPoint.data.dominant_pause_type}`] || '#f8f9fa',
                                                color: '#666'
                                            }
                                        }}
                                    >
                                        {pauseLabels[hoveredPoint.data.dominant_pause_type] || 'Звичайна'}
                                    </Badge>
                                </Group>
                            </>
                        )}
                    </Stack>
                </Paper>
            )}

            <svg
                ref={svgRef}
                viewBox={`0 0 ${width} ${height}`}
                preserveAspectRatio="none"
                style={{width: '100%', height: `${height}px`, display: 'block', cursor: 'crosshair'}}
                onMouseMove={handleMouseMove}
                onMouseLeave={() => setHoveredPoint(null)}
            >
                <defs>
                    <linearGradient id="gradientPace" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#4dabf7" stopOpacity="0.4"/>
                        <stop offset="100%" stopColor="#4dabf7" stopOpacity="0"/>
                    </linearGradient>
                </defs>

                {gridLines}
                <path d={areaPath} fill="url(#gradientPace)"/>
                <path d={linePath} fill="none" stroke="#228be6" strokeWidth="2" strokeLinejoin="round"/>

                {hoveredPoint && (
                    <line
                        x1={hoveredPoint.x}
                        y1="0"
                        x2={hoveredPoint.x}
                        y2={height}
                        stroke="#228be6"
                        strokeWidth="1"
                        strokeDasharray="4 2"
                    />
                )}

                {hoveredPoint && (
                    <circle
                        cx={hoveredPoint.x}
                        cy={hoveredPoint.y}
                        r="4"
                        fill="white"
                        stroke="#228be6"
                        strokeWidth="2"
                    />
                )}
            </svg>

            <Box mt="xs" style={{position: 'relative', height: '20px'}}>
                {[0, 0.25, 0.5, 0.75, 1].map((pos) => {
                    const pointIndex = Math.floor(pos * (graph.length - 1));
                    const timeMs = graph[pointIndex]?.timestamps_total_ms || 0;
                    return (
                        <Text
                            key={pos}
                            size="xs"
                            c="dimmed"
                            style={{
                                position: 'absolute',
                                left: `${pos * 100}%`,
                                transform: 'translateX(-50%)',
                                whiteSpace: 'nowrap'
                            }}
                        >
                            {formatTime(timeMs)}
                        </Text>
                    );
                })}
            </Box>
        </Box>
    );
};
