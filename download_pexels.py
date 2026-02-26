import os
import time
import requests

# --- CONFIGURATION ---
# IMPORTANT: Put your free Pexels API Key here
PEXELS_API_KEY = "API_KEY_HERE" 

# Categories of your choice
CATEGORIES = ["street dance", "boxing", "ballet", "martial arts"]

# How many videos to download per category
# 40 per category = 160 videos total. This keeps you safely under the 200 req/hour limit.
VIDEOS_PER_CATEGORY = 40 

# Base directory to save the dataset
SAVE_DIR = "./unlicensed_motion_dataset"

HEADERS = {
    "Authorization": PEXELS_API_KEY
}

def download_video(url, save_path):
    """Streams the video download to avoid RAM overload."""
    try:
        response = requests.get(url, stream=True, timeout=15)
        response.raise_for_status()
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return False

def fetch_category_videos(query):
    """Hits the Pexels API to get video URLs for a specific category."""
    search_url = f"https://api.pexels.com/videos/search?query={query}&per_page={VIDEOS_PER_CATEGORY}&orientation=landscape"
    
    print(f"\n--- Searching for: {query} ---")
    response = requests.get(search_url, headers=HEADERS)
    
    if response.status_code != 200:
        print(f"API Error {response.status_code}: {response.text}")
        return []

    data = response.json()
    videos = data.get("videos", [])
    
    download_links = []
    for vid in videos:
        vid_id = vid.get("id")
        # Grab the highest quality HD file available
        video_files = vid.get("video_files", [])
        hd_files = [f for f in video_files if f.get("quality") == "hd"]
        
        if hd_files:
            # Sort by width to get a good resolution, but not necessarily massive 4k files
            hd_files.sort(key=lambda x: x.get("width", 0), reverse=True)
            download_links.append((vid_id, hd_files[0]["link"]))
        elif video_files:
            # Fallback to whatever is available
            download_links.append((vid_id, video_files[0]["link"]))

    return download_links

def main():
    if PEXELS_API_KEY == "YOUR_PEXELS_API_KEY":
        print("ERROR: Please add your Pexels API Key to the script!")
        return

    os.makedirs(SAVE_DIR, exist_ok=True)

    for category in CATEGORIES:
        category_dir = os.path.join(SAVE_DIR, category.replace(" ", "_"))
        os.makedirs(category_dir, exist_ok=True)
        
        video_links = fetch_category_videos(category)
        print(f"Found {len(video_links)} videos for '{category}'. Starting download...")
        
        for idx, (vid_id, link) in enumerate(video_links):
            save_path = os.path.join(category_dir, f"{vid_id}.mp4")
            
            # Skip if already downloaded (useful if the script crashes and you restart it)
            if os.path.exists(save_path):
                print(f"[{idx+1}/{len(video_links)}] Already exists: {vid_id}.mp4")
                continue
                
            print(f"[{idx+1}/{len(video_links)}] Downloading {vid_id}.mp4...")
            success = download_video(link, save_path)
            
            # Sleep slightly to be polite to the server and avoid rate limit spikes
            if success:
                time.sleep(1)

    print("\n✅ All downloads complete!")

if __name__ == "__main__":
    main()
