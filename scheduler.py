# janus_scheduler/engine/scheduler.py

import random
from .components import Task, CPUCore # The '.' is important, it means import from the same package

class SoC:
    """The main System on a Chip class that manages all components and runs the simulation."""
    def __init__(self, num_p_cores, num_e_cores, num_tasks):
        # Create the CPU cores
        self.p_cores = [CPUCore(core_id=i, core_type="P-core") for i in range(num_p_cores)]
        self.e_cores = [CPUCore(core_id=i + num_p_cores, core_type="E-core") for i in range(num_e_cores)]
        self.all_cores = self.p_cores + self.e_cores
        
        # Prepare task lists
        self.master_task_list = self.generate_tasks(num_tasks)
        self.task_queue = [] # Tasks that have arrived but are not yet assigned
        self.completed_tasks = []

        # Simulation state
        self.current_tick = 0
        self.total_power_consumed = 0.0

    def generate_tasks(self, num_tasks):
        """Generates a list of tasks with varying arrival times."""
        tasks = []
        for i in range(num_tasks):
            # Tasks will arrive at staggered times
            arrival_time = random.randint(0, num_tasks * 5)
            tasks.append(Task(task_id=i, arrival_time=arrival_time))
        # Sort tasks by arrival time
        tasks.sort(key=lambda x: x.arrival_time)
        return tasks

    def check_for_new_arrivals(self):
        """Checks if any tasks have arrived at the current tick and adds them to the queue."""
        while self.master_task_list and self.master_task_list[0].arrival_time <= self.current_tick:
            task = self.master_task_list.pop(0)
            print(f"Tick {self.current_tick}: ==> Task-{task.id} ({task.type}) has arrived.")
            self.task_queue.append(task)
            
    def schedule_rule_based(self):
        """A simple, rule-based scheduler to assign tasks from the queue."""
        # Don't do anything if there are no tasks in the queue
        if not self.task_queue:
            return

        # Try to assign tasks to idle cores
        for core in self.all_cores:
            if core.current_task and core.current_task.is_finished():
                print(f"Tick {self.current_tick}: <== Task-{core.current_task.id} has finished on Core-{core.id}.")
                self.completed_tasks.append(core.current_task)
                core.current_task = None # Free up the core

            if core.current_task is None and self.task_queue:
                task_to_assign = None
                
                # --- SCHEDULER LOGIC ---
                # Rule 1: Try to find the "best" task for the current core type
                if core.type == "P-core":
                    # P-cores prefer CPU-Bound tasks
                    for task in self.task_queue:
                        if task.type == "CPU-Bound":
                            task_to_assign = task
                            break
                else: # E-core
                    # E-cores prefer I/O-Bound tasks
                    for task in self.task_queue:
                        if task.type == "I/O-Bound":
                            task_to_assign = task
                            break
                
                # Rule 2: If no "best" task is found, just take any task to keep cores busy
                if not task_to_assign and self.task_queue:
                    task_to_assign = self.task_queue[0]
                
                # --- ASSIGNMENT ---
                if task_to_assign:
                    self.task_queue.remove(task_to_assign)
                    core.assign_task(task_to_assign)
                    print(f"Tick {self.current_tick}: --> Assigning Task-{task_to_assign.id} to Core-{core.id}.")


    def run_simulation_tick(self):
        """Executes a single step of the simulation."""
        # 1. Check for new tasks arriving
        self.check_for_new_arrivals()

        # 2. Run the scheduler to assign tasks
        self.schedule_rule_based()
        
        # 3. Tick every core to process tasks and update temps
        for core in self.all_cores:
            core.tick()
            self.total_power_consumed += core.get_current_power_draw()

        # 4. Increment simulation time
        self.current_tick += 1

    def print_final_stats(self):
        """Prints a summary of the simulation results."""
        print("\n--- Simulation Finished ---")
        print(f"Total Ticks: {self.current_tick}")
        print(f"Total Tasks Completed: {len(self.completed_tasks)}")
        print(f"Total Power Consumed: {self.total_power_consumed:.2f} units")
        
        # Calculate average task completion time
        total_time = sum((task.arrival_time for task in self.completed_tasks))
        avg_time = (self.current_tick - (total_time / len(self.completed_tasks))) if self.completed_tasks else 0
        print(f"Average Task Turnaround Time: {avg_time:.2f} ticks")