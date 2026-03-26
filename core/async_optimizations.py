
# Async performance optimizations
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List

class AsyncOptimizations:
    """Async performance optimization utilities"""
    
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
        
    async def run_in_thread(self, func, *args, **kwargs):
        """Run CPU-intensive tasks in thread pool"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, func, *args, **kwargs)
        
    async def batch_operations(self, operations: List, batch_size: int = 10):
        """Process operations in batches for better performance"""
        results = []
        for i in range(0, len(operations), batch_size):
            batch = operations[i:i + batch_size]
            batch_results = await asyncio.gather(*batch, return_exceptions=True)
            results.extend(batch_results)
        return results
