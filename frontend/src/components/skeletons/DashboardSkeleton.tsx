import React from 'react';
import { Box, Skeleton, Grid, Card, CardContent } from '@mui/material';

const DashboardSkeleton: React.FC = () => {
	return (
		<Box sx={{ p: 2 }}>
			<Skeleton variant="text" width={220} height={40} />
			<Grid container spacing={2} sx={{ mt: 1 }}>
				{[...Array(3)].map((_, i) => (
					<Grid item xs={12} md={4} key={i}>
						<Card>
							<CardContent>
								<Skeleton variant="text" width="60%" />
								<Skeleton variant="rectangular" height={120} sx={{ mt: 1 }} />
							</CardContent>
						</Card>
					</Grid>
				))}
			</Grid>
		</Box>
	);
};

export default DashboardSkeleton;
