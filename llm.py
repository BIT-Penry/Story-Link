import time
from google import genai
from google.genai import types

# 方法 1: 直接在 Client 初始化时传入 API KEY
client = genai.Client(api_key="AIzaSyD91kz0udBl80_u8dcmObWfAMh25Uqpjjg")

# 或者方法 2: 使用 configure 方法
# genai.configure(api_key="你的_GOOGLE_API_KEY")
# client = genai.Client()

prompt = prompt = """A realistic, tense moment between two archaeologists in a dark underground tomb:
Close-up shot of MING (Asian male, mid-20s, dirty face, wearing expedition headlamp and dusty jacket), his hand pressed against an ancient stone wall covered with faintly glowing blue symbols. His eyes are wide, pupils dilated with excitement and fear. Sweat beads visible on his forehead.
Beside him, XIAOYU (Asian female, mid-20s, similar gear, holding an orange-flamed torch) looks at him with concern and determination. Her jaw is set, ready to make a hard decision.
The torch casts warm, flickering orange light on their faces from the left, while cold blue light from the mysterious symbols illuminates them from the right, creating dramatic contrast.
In soft focus background: wet stone walls, water dripping, scattered old equipment on the ground.
MING whispers urgently: "We're so close to understanding everything..."
XIAOYU firmly grips his shoulder: "Some doors should stay closed."
Natural lighting, cinematic composition, photorealistic, emotional tension, Indiana Jones meets Arrival aesthetic. 4K quality."""

operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    prompt=prompt,
)

# Poll the operation status until the video is ready.
while not operation.done:
    print("Waiting for video generation to complete...")
    time.sleep(10)
    operation = client.operations.get(operation)

# Download the generated video.
generated_video = operation.response.generated_videos[0]
client.files.download(file=generated_video.video)
generated_video.video.save("dialogue_example.mp4")
print("Generated video saved to dialogue_example.mp4")