import subprocess
import time


start_time = time.time()
# command = ["python", "scripts/run.py", "--load_snapshot", f"data/nerf/1_car2/1_car2.ingp", "--screenshot_transforms", f"data/nerf/1_car2/transforms.json", "--screenshot_dir", "data/nerf/1_car2", "--screenshot_spp", "1", "--screenshot_frames", "1"]
command = ["python", "scripts/run.py", "--load_snapshot", f"data/nerf/1_car2/1_car2.ingp", "--screenshot_transforms", f"data/nerf/1_car2/transforms.json", "--screenshot_dir", "data/nerf/1_car2", "--screenshot_spp", "1", "--screenshot_frames", "1","2","3","4","5"]
subprocess.run(command)
end_time = time.time()
execution_time = end_time - start_time
print(f"Execution time: {execution_time} seconds")
