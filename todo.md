- Change project structure so that's not just a big file
- Add a little check at the bottom of images on grid that are already labeled. It should not only check if lable file exist, it should also check if it's empty.
- Fix the zooming, it's wierd. Look for a concept of anchoring the image.
- The image centering when loaded is not working under certain scenarios, investigate that.
- Show the image name the bottom of the page when viewing it.


TODO for far future.
- Add option to select label for that selection (might need DB implementation)
    - Sugestion:
    - The labels can be listed at the bottom as a list; when you click a specific one, the label changes color.
    - With the label selected, there should be a button (or shortcut) that opens a modal with a list and I can select a label for that B.B. or can create a new one.
