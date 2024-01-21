export default async function getSingleImage(id) {
  try {
    const response = await fetch(`/api/getSingleImage?id=${id}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch image: ${response.statusText}`);
    }
    const image = await response.json();
    return image;
  } catch (error) {
    console.error("Error fetching image:", error);
    return null;
  }
}
