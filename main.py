# janus_scheduler/main.py

from engine.scheduler import SoC

def main():
    """Main function to run the simulation."""
    print("--- Starting Janus Scheduler Simulation (Text-Based) ---")
    
    # Simulation Parameters
    NUM_P_CORES = 2
    NUM_E_CORES = 4
    NUM_TASKS = 20
    MAX_TICKS = 1000 # To prevent infinite loops

    # Create and run the SoC
    soc = SoC(NUM_P_CORES, NUM_E_CORES, NUM_TASKS)
    
    # Main simulation loop
    while len(soc.completed_tasks) < NUM_TASKS and soc.current_tick < MAX_TICKS:
        soc.run_simulation_tick()
        # Optional: Print status every 10 ticks for readability
        if soc.current_tick % 10 == 0:
            print("-----------------------------------------------------")
            for core in soc.all_cores:
                print(core)
            print(f"Task Queue: {[f'Task-{t.id}' for t in soc.task_queue]}")
            print("-----------------------------------------------------")

    soc.print_final_stats()

if __name__ == "__main__":
    main()