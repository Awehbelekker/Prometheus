import React from 'react';
import { Box, Skeleton, Grid } from '@mui/material';

const HRMSkeleton: React.FC = () => {
	return (
		<Box sx={{ p: 2 }}>
			<Skeleton variant="text" width={220} height={40} />
			<Grid container spacing={2} sx={{ mt: 1 }}>
				{[...Array(6)].map((_, i) => (
					<Grid item xs={12} sm={6} md={4} key={i}>
						<Skeleton variant="rectangular" height={120} />
					</Grid>
				))}
			</Grid>
		</Box>
	);
};

export default HRMSkeleton;
