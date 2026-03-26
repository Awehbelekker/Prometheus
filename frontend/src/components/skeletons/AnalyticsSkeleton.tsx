import React from 'react';
import { Box, Skeleton, Grid, Card, CardContent } from '@mui/material';

const AnalyticsSkeleton: React.FC = () => {
	return (
		<Box sx={{ p: 2 }}>
			<Skeleton variant="text" width={260} height={40} />
			<Grid container spacing={2} sx={{ mt: 1 }}>
				{[...Array(2)].map((_, i) => (
					<Grid item xs={12} md={6} key={i}>
						<Card>
							<CardContent>
								<Skeleton variant="text" width="50%" />
								<Skeleton variant="rectangular" height={200} sx={{ mt: 1 }} />
							</CardContent>
						</Card>
					</Grid>
				))}
			</Grid>
		</Box>
	);
};

export default AnalyticsSkeleton;
