/**
 * Fetches a single image from the server.
 *
 * @param {string} id - The ID of the image to fetch.
 * @returns {Promise<Object|null>} - A promise that resolves to the image object, or null if there is an error.
 * @throws {Error} - If there is an error fetching the image.
 */
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
