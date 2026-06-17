# known_faces — Sample Folder Structure

This folder shows how to organise your known faces for FACE-TRACK.

## How to add people

Create one subfolder per person inside `known_faces/`. The folder name becomes the person's display name in the system.

```
known_faces/
├── Alice_Smith/
│   ├── photo1.jpg
│   └── photo2.jpg
├── Bob_Jones/
│   └── photo1.jpg
└── sample/          ← this folder (example structure)
    └── README.md
```

## Photo guidelines for best accuracy

- ✅ Clear, front-facing photo
- ✅ Good lighting, no heavy shadows
- ✅ Face takes up at least 30% of the image
- ✅ JPG or PNG format
- ❌ Avoid sunglasses, masks, or heavy blur
- ❌ Avoid group photos (one person per photo)

## Adding via UI

You can also register people directly from the Streamlit app:
1. Open http://localhost:8501
2. Go to the sidebar → "Register Person"
3. Enter the name and upload a photo
4. Click "Register" — done!
