Prompt Update - dialogue

- More dialogues to lead character's emotions and lead story
- Multiple dialogue in a scene is allowed, write it in an order

- Current prompt keep creating 1:1 image
  We must create Vertical 9:16 ratio image

Frontend UI update

- Chat bubble with opacity 30%
  - Text shouldn't have opacity
- Dark Gray boarder
- bubble should be moveable after located over image

Prompt Update - Camera
scene_image_generate

- Camera setting in "Scene image" should be stronger: current output image tend to 'follow' the provided camera setting, but not so strong. we need to put more weight on camera.
  webtoon_writer: - Should allow multiple camera setting where it makes sense. e.g) ovet-the-shoulder-view, wide-angle

Prompt Update - Camera
webtoon_writer:

- writer should add "SFX" effect to each scene, should define where it can empower the mood and story-delivery. SFX effect should be described with detail

scene_image_generate

- Prompt should be updated to take SFX information from webtoon_writer, and apply the SFX visually well on image creating

Dialogue Chat bubble

- No Name on the top: chat-bubble should only include the dialogue.

** Expensive feature update **
This can be separte, and can be handled at the very end.

When there is a multiple dialogue in a scene, I would like to who each dialogue over the image
each dialogue shows up, with 1 second term for now ( I may want to adjust this later) so user put 'location' of each chat bubble.
in the video
image stay ------------
chat bubble 1 -> chat bubble 2 -> ...
