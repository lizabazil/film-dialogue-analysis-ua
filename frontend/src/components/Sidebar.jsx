import { Stack, Tooltip, UnstyledButton, rem } from '@mantine/core';
import { IconFileUpload, IconGraph } from '@tabler/icons-react';
import {useLocation, useNavigate} from "react-router-dom";

function NavbarLink({ icon: Icon, label, active, onClick }) {
  return (
    <Tooltip label={label} position="right" transitionProps={{ duration: 0 }}>
      <UnstyledButton
        onClick={onClick}
        style={{
          width: rem(50),
          height: rem(50),
          borderRadius: rem(10),
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: active ? 'var(--mantine-color-violet-7)' : 'var(--mantine-color-gray-7)',
          backgroundColor: active ? 'var(--mantine-color-violet-0)' : 'transparent',
          transition: 'all 0.2s ease', // Soft UI smooth transition
        }}
      >
        <Icon style={{ width: rem(24), height: rem(24) }} stroke={1.5} />
      </UnstyledButton>
    </Tooltip>
  );
}

export function Sidebar() {
const navigate = useNavigate();
  const location = useLocation();

  const links = [
    { icon: IconFileUpload, label: 'Upload', path: '/' },
    { icon: IconGraph, label: 'Analytics', path: '/analytics' },
  ];

  return (
    <nav style={{
      width: rem(80),
      height: '100vh',
      padding: '20px',
      borderRight: '1px solid #eee',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      backgroundColor: '#fff'
    }}>
<Stack justify="center" gap={10}>
        {links.map((link) => (
          <NavbarLink
            {...link}
            key={link.label}
            active={location.pathname === link.path}
            onClick={() => navigate(link.path)}
          />
        ))}
      </Stack>    </nav>
  );
}