# janus_scheduler/engine/components.py

import random

# --- Enhanced Component Classes ---

class Task:
    """Represents a more realistic task with detailed properties."""
    def __init__(self, task_id, arrival_time):
        self.id = task_id
        self.arrival_time = arrival_time # The simulation tick when this task appears
        
        # Determine if a task is CPU-bound or I/O-bound
        is_cpu_bound = random.random() > 0.5
        if is_cpu_bound:
            self.type = "CPU-Bound"
            self.total_cycles = random.randint(200, 500) # Needs a lot of computation
            self.io_frequency = 0 # Rarely waits for I/O
        else:
            self.type = "I/O-Bound"
            self.total_cycles = random.randint(50, 100) # Less computation
            self.io_frequency = random.randint(3, 8) # Pauses for I/O often

        self.cycles_done = 0
        self.io_wait_timer = 0 # How long the task has to wait for I/O

    def is_finished(self):
        return self.cycles_done >= self.total_cycles

    def is_waiting_for_io(self):
        return self.io_wait_timer > 0

    def work(self, cycles_to_do):
        """Perform work on the task and handle I/O events."""
        if self.is_waiting_for_io():
            self.io_wait_timer -= 1
            return
            
        self.cycles_done += cycles_to_do

        # Check if an I/O event occurs
        if self.type == "I/O-Bound" and random.randint(1, 100) < self.io_frequency:
            self.io_wait_timer = random.randint(5, 10) # Set I/O wait time

    def __repr__(self):
        return f"Task-{self.id}({self.type}, {self.cycles_done}/{self.total_cycles})"


class CPUCore:
    """Represents a core with thermal properties."""
    def __init__(self, core_id, core_type="E-core"):
        self.id = core_id
        self.type = core_type
        self.current_task = None
        
        # Performance, Power, and Thermal properties
        if self.type == "P-core":
            self.base_speed = 2.0
            self.power_draw = 4.0
            self.heat_generation = 0.8 # Generates more heat
        else:
            self.base_speed = 1.0
            self.power_draw = 1.0
            self.heat_generation = 0.2 # Generates less heat

        self.idle_power_draw = 0.1
        self.temperature = 25.0 # Starting temperature
        self.max_temp = 90.0 # Throttling threshold
        self.cooling_factor = 0.4 # How quickly it cools down

    def get_current_speed(self):
        """Returns the core's speed, adjusted for thermal throttling."""
        if self.temperature >= self.max_temp:
            # Drastically reduce speed if overheating
            return self.base_speed * 0.5 
        return self.base_speed

    def get_current_power_draw(self):
        """Returns the current power draw based on the core's state."""
        # A core is considered "active" if it has a task AND that task is not waiting for I/O
        is_active = self.current_task is not None and not self.current_task.is_waiting_for_io()
        
        if is_active:
            return self.power_draw
        else:
            return self.idle_power_draw

    def update_temperature(self):
        """Updates the core's temperature based on its state."""
        # A core is active and generating heat only if its task is NOT waiting for I/O
        is_active_computing = self.current_task is not None and not self.current_task.is_waiting_for_io()
        
        if is_active_computing:
            self.temperature += self.heat_generation
        else:
            # Cool down if idle OR if the task is waiting for I/O
            self.temperature -= self.cooling_factor
        
        # Ensure temperature doesn't drop below ambient
        self.temperature = max(25.0, self.temperature)

    def assign_task(self, task):
        self.current_task = task

    def tick(self):
        """A single time step for the core."""
        self.update_temperature()
        if self.current_task:
            if self.current_task.is_finished():
                self.current_task = None
                return
            
            if self.current_task.is_waiting_for_io():
                # If task is waiting for I/O, the core is effectively idle
                pass
            else:
                # Do work
                speed = self.get_current_speed()
                self.current_task.work(speed)

    def __repr__(self):
        status = "Idle" if not self.current_task else f"Running {self.current_task}"
        return f"Core-{self.id}({self.type}) Temp:{self.temperature:.1f}°C | {status}"