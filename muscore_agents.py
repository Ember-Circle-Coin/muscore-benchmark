import time
import numpy as np

def run_simulation_2d(grid_size, label):
    start = time.perf_counter()
    
    # 2D grid — each cell is a 16-bit packed agent
    agents = np.random.randint(0, 65535, (grid_size, grid_size), dtype=np.uint16)
    
    collapses = 0
    clusters = 0
    
    for cycle in range(100):
        energy = (agents >> 8) & 0xFF
        
        # 2D neighbours — up, down, left, right
        up    = np.roll(energy, 1,  axis=0)
        down  = np.roll(energy, -1, axis=0)
        left  = np.roll(energy, 1,  axis=1)
        right = np.roll(energy, -1, axis=1)
        
        neighbour_avg = (up + down + left + right) // 4
        energy_delta  = energy.astype(np.int16) - neighbour_avg.astype(np.int16)
        
        collapse_mask = (energy < 25) | (np.abs(energy_delta) > 60)
        collapses += np.sum(collapse_mask)
        
        new_energy = np.where(
            collapse_mask,
            neighbour_avg,
            np.clip(energy + energy_delta // 4, 0, 255)
        ).astype(np.uint8)
        
        agents = (agents & 0x00FF) | (new_energy.astype(np.uint16) << 8)
        
        if cycle % 25 == 0:
            clusters += np.sum((energy > 180) & (up > 180) & (left > 180))
    
    elapsed = (time.perf_counter() - start) * 1000
    total_agents = grid_size * grid_size
    
    print(f"\n{label}")
    print(f"  Grid:          {grid_size}x{grid_size}")
    print(f"  Agents:        {total_agents:>12,}")
    print(f"  Collapses:     {collapses:>12,}")
    print(f"  Clusters:      {clusters:>12,}")
    print(f"  Time:          {elapsed:>10.1f}ms")
    print(f"  Collapse rate: {collapses/total_agents:.2f} per agent")
    
    return collapses, clusters, elapsed

if __name__ == "__main__":
    print("MUSCORE 2D AGENT SIMULATION")
    print("Spatial grid — emergence requires space")
    print("=" * 50)
    
    c1, cl1, t1 = run_simulation_2d(100,  "Standard  (100x100  = 10k agents)")
    c2, cl2, t2 = run_simulation_2d(1000, "MusCoRe   (1000x1000 = 1M agents)")
    
    print()
    print("=" * 50)
    print(f"Resolution:    100x more agents")
    print(f"Time ratio:    {t2/t1:.1f}x")
    print(f"Cluster ratio: {cl2/(cl1+1):.1f}x")
    print()
    print("2D space allows patterns 1D cannot form.")
