import React from 'react';
import { Box, Skeleton, Card, CardContent } from '@mui/material';

const LiveTradingSkeleton: React.FC = () => {
	return (
		<Box sx={{ p: 2 }}>
			<Skeleton variant="text" width={240} height={40} />
			<Card sx={{ mt: 2 }}>
				<CardContent>
					<Skeleton variant="rectangular" height={180} />
					<Skeleton variant="text" width="40%" sx={{ mt: 2 }} />
				</CardContent>
			</Card>
		</Box>
	);
};

export default LiveTradingSkeleton;
