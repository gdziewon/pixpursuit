"use client";

import {BoxOverlay} from "@/utils/faceBoxes";
import { useState, useEffect, useRef } from "react";
import { ArrowDownTrayIcon, XCircleIcon, EyeIcon, HeartIcon, PlusIcon, PencilIcon, XMarkIcon, CheckIcon, HandThumbDownIcon, HandThumbUpIcon} from "@heroicons/react/24/solid";
import getSingleImage from "@/utils/getSingleImage";
import Loading from "@/app/loading";
import {useSession} from "next-auth/react";
import axios from "axios";
import Image from "next/image";
import Link from "next/link";

export default function ImagePage({ params }) {
  const [newTag, setNewTag] = useState(null);
  const [editingDescription, setEditingDescription] = useState(false);
  const [editedDescription, setEditedDescription] = useState("");
  const { data: session } = useSession();
  const [hoveredTag, setHoveredTag] = useState(null);
  const [leaveTimer, setLeaveTimer] = useState(null);
  const [originalSize, setOriginalSize] = useState({ width: 0, height: 0 });
  const id = params.id;
  const [image, setImage] = useState(null);
  const [likes, setLikes] = useState(0);
  const [isLikedByUser, setIsLikedByUser] = useState(false);
  const [autoTagsFeedback, setAutoTagsFeedback] = useState({});
  const hasAddedView = useRef(false)
  const [similarImages, setSimilarImages] = useState([]);
  const [isSimilarImagesLoading, setSimilarImagesLoading] = useState(true);
  const [isHovered, setIsHovered] = useState(false);


  useEffect(() => {
    const fetchImage = async () => {
      const imageData = await getSingleImage(id);
      setImage(imageData);
      setLikes(imageData.likes);
      setIsLikedByUser(session && session.user ? imageData.liked_by.includes(session.user.name) : false);
      setEditedDescription(imageData.description);
      const img = new window.Image();
      img.onload = () => {
        setOriginalSize({ width: img.naturalWidth, height: img.naturalHeight });
      };
      img.src = imageData.image_url;

      if (session && session.user && imageData.feedback_history && imageData.feedback_history[session.user.name]) {
        setAutoTagsFeedback(imageData.feedback_history[session.user.name]);
      }
    };
    fetchImage();
  }, [id, session]);

  useEffect(() => {
    const addView = async () => {
      try {
        const viewData = {
          inserted_id: id,
        };
        console.log('Adding view for image id:', id);
        const response = await axios.post('http://localhost:8000/add-view', viewData, {
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (response.status !== 200) {
          console.error('Failed to add view');
        }
      } catch (error) {
        console.error('Error adding view:', error);
      }
    };
    if (id && !hasAddedView.current) {
        addView(id);
        hasAddedView.current = true;
    } else {
      hasAddedView.current = false;
    }
  }, [id]);

  useEffect(() => {
    const fetchSimilarImages = async () => {
      try {
        setSimilarImagesLoading(true); // Start loading
        const response = await axios.post('http://localhost:8000/find-similar-images', {
          image_id: id,
          limit: 10,
        });

        if (response.status === 200) {
          setSimilarImages(response.data.similar_images);
        } else {
          console.error('Failed to fetch similar images');
        }
      } catch (error) {
        console.error('Error fetching similar images:', error);
      } finally {
        setSimilarImagesLoading(false);
      }
    };

    fetchSimilarImages();
  }, [id]);

  async function downloadImage(url, filename) {
    try {
      const response = await fetch(`http://localhost:8000/download-image?url=${encodeURIComponent(url)}`);
      if (!response.ok) alert('Failed to download image');

      const reader = response.body.getReader();
      const stream = new ReadableStream({
        async start(controller) {
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            controller.enqueue(value);
          }
          controller.close();
          reader.releaseLock();
        }
      });

      new Response(stream).blob().then(blob => {
        const blobUrl = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = blobUrl;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(blobUrl);
      });
    } catch (error) {
      console.error('Error in downloadImage function:', error);
    }
  }

  const renderDescription = () => {
    if (editingDescription) {
      return (
          <div>
            <div>
                        <textarea
                            className="w-full rounded border bg-gray-900 text-white px-3 py-1 text-lg shadow-md"
                            value={editedDescription}
                            onChange={handleDescriptionChange}
                            rows="3"
                            style={{resize: "vertical"}}
                        />
            </div>
            <div className="mt-2">
              <button
                  className="rounded border bg-red-200 px-3 py-1 text-sm text-red-700 mr-2"
                  onClick={handleCancelEdit}
              >
                <XMarkIcon className="h-5 w-5"/>
              </button>
              <button
                  className="rounded border bg-green-200 px-3 py-1 text-sm text-green-700"
                  onClick={handleChangeDescription}
              >
                <CheckIcon className="h-5 w-5"/>
              </button>
            </div>
          </div>
      );
    } else {
      return (
          <div
              onMouseEnter={() => setIsHovered(true)}
              onMouseLeave={() => setIsHovered(false)}
          >
            <h1 className="text-2xl text-gray-900 dark:text-white mb-4" style={{color: 'white'}}>
              {image.description || 'No description.'}
            </h1>
            {session && isHovered && (
                <button
                    className="inline-flex items-center bg-gray-200 rounded-full px-3 py-1 text-sm font-semibold text-gray-800 ml-2 hover:bg-gray-400 transition-colors duration-200 ease-in-out"
                    onClick={toggleEditingDescription}
                >
                  <PencilIcon className="h-5 w-5 mr-2"/> {image.description ? 'Edit Description' : 'Add Description'}
                </button>
            )}
          </div>
      );
    }
  };

  const renderHeartIcon = () => {
    const heartIconClass = session
        ? `h-10 w-10 ${isLikedByUser ? 'text-red-500 cursor-pointer' : 'text-gray-500 hover:text-pink-500 cursor-pointer'}`
        : 'h-10 w-10 text-pink-500';

    return (
        <HeartIcon
            onClick={session ? () => handleHeartClick(!isLikedByUser) : undefined}
            className={heartIconClass}
        />
    );
  };

  const handleAddTag = async () => {
    try {
      const tagData = {
        inserted_id: id,
        tags: [newTag],
      };

      const response = await axios.post('http://localhost:8000/add-user-tag', tagData, {
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${session.accessToken}`,
        },
      });

      if (response.status === 200) {
        alert("Tag added successfully");
        setImage(prev => ({ ...prev, user_tags: [...prev.user_tags, newTag] }));
        setNewTag(""); // Clear the input field
      } else {
        alert("Failed to add tag");
      }
    } catch (error) {
      alert("Error adding tag");
      console.error(error);
    }
  };

  const handleHeartClick = async (isPositive) => {
    try {
      const faceData = {
        inserted_id: id,
        is_positive: isPositive,
      };

      const response = await axios.post('http://localhost:8000/add-like', faceData, {
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${session.accessToken}`,
        },
      });

      if (response.status === 200) {
        alert(isPositive ? 'Like submitted successfully' : 'Unlike submitted successfully');
        setLikes(isPositive ? likes + 1 : likes - 1);
        setIsLikedByUser(isPositive);
      } else {
        alert('Failed to submit like');
      }
    } catch (error) {
      alert('Error submitting like:', error);
    }
  }

  const handleChangeDescription = async () => {
    const descriptionData = {
      inserted_id: id,
      description: editedDescription
    };

    try {
      const response = await axios.post('http://localhost:8000/add-description', descriptionData, {
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${session.accessToken}`,
        },
      });

      if (response.status === 200) {
        alert("Description updated successfully");
        setImage(prev => ({ ...prev, description: editedDescription }));
      } else {
        alert("Failed to update description");
      }
    } catch (error) {
      alert("Error updating description");
      console.error(error);
    }

    setEditingDescription(false);
  };

  const handleRemoveTag = async (tagToRemove) => {
    try {
      const tagData = {
        image_id: id,
        tags: [tagToRemove],
      };

      const response = await axios.post('http://localhost:8000/remove-tags', tagData, {
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${session.accessToken}`,
        },
      });

      if (response.status === 200) {
        alert("Tag removed successfully");
        setImage(prev => ({
          ...prev,
          user_tags: prev.user_tags.filter(tag => tag !== tagToRemove)
        }));
      } else {
        alert("Failed to remove tag");
      }
    } catch (error) {
      alert("Error removing tag");
      console.error(error);
    }
  };

  const sendTagFeedback = async (tag, isPositive) => {
    try {
      const feedbackData = {
        inserted_id: id,
        tag: tag,
        is_positive: isPositive
      };

      const response = await axios.post('http://localhost:8000/feedback-on-tags', feedbackData, {
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${session.accessToken}`,
        },
      });

      if (response.status === 200) {
        alert("Feedback submitted successfully");
        setAutoTagsFeedback(prev => ({ ...prev, [tag]: isPositive }));
      } else {
        alert("Failed to submit feedback");
      }
    } catch (error) {
      console.error("Error submitting feedback:", error);
      alert("Error submitting feedback");
    }
  };

  const checkFeedbackHistory = (tag) => {
    return autoTagsFeedback[tag] !== undefined ? autoTagsFeedback[tag] : null;
  };

  const handleMouseEnter = (tag) => {
    if (leaveTimer) {
      clearTimeout(leaveTimer);
      setLeaveTimer(null);
    }
    setHoveredTag(tag);
  };

  const handleMouseLeave = () => {
    const timer = setTimeout(() => {
      setHoveredTag(null);
    }, 1000); // Delay before hiding buttons
    setLeaveTimer(timer);
  };

  const handleDescriptionChange = (e) => {
    setEditedDescription(e.target.value);
  };

  const toggleEditingDescription = () => {
    setEditingDescription(!editingDescription);
  };

  const handleCancelEdit = () => {
    setEditingDescription(false);
    setEditedDescription(image.description);
  };




  if (!image) {
    return <Loading />;
  }

  return (
      <main className="flex flex-col p-6">
        <div className="flex">
          <div className="w-1/2">
            <div className="flex justify-center flex-col">
              <BoxOverlay image={image} boxes={image.embeddings_box || []} originalSize={originalSize}
                          session={session}/>
            </div>
            <div className="flex justify-between items-center">
              <div>
                {image.metadata.DateTime && <p className="">Taken: {image.metadata.DateTime}</p>}
                <p>Added by: {image.added_by}</p>
                <p className="flex items-center">
                  <EyeIcon className="h-5 w-5 mr-1"/>
                  {image.views}
                </p>
              </div>
              <Link href={`/albums/${image.album_id}`}>
                <div className="mt-2 inline-flex items-center px-2 py-1 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-gray-400 hover:bg-gray-600">
                  Go to album
                </div>
              </Link>
              <div className="flex items-center">
                <p className="ml-2">{likes}</p>
                {renderHeartIcon()}
                <ArrowDownTrayIcon
                    className="h-6 w-6 text-blue-500 hover:text-blue-700 cursor-pointer ml-2"
                    onClick={() => downloadImage(image.image_url, image.filename)}
                />
              </div>
            </div>
          </div>
          <div className="w-1/2 pl-6">
            <h1 className="text-3xl font-bold text-teal-100 dark:text-white mb-4">
              Photo description:
            </h1>
            {renderDescription()}
            <h1 className="text-3xl font-bold text-teal-100 dark:text-white mb-4">
              Tags:
            </h1>
            <div className="flex flex-wrap gap-2 mb-4">
              {image &&
                  Array.isArray(image.detected_objects) &&
                  image.detected_objects.map((object, index) => (
                      <span
                          key={index}
                          className="inline-block bg-yellow-200 rounded-full px-3 py-1 text-sm font-semibold text-yellow-700 mr-2"
                      >
        {object}
      </span>
                  ))}
            </div>
            <div className="flex flex-wrap gap-2 mb-4">
              {image && Array.isArray(image.auto_tags) && image.auto_tags.map((tag, index) => {
                const feedback = checkFeedbackHistory(tag);

                return (
                    <div
                        key={index}
                        onMouseEnter={() => handleMouseEnter(tag)}
                        onMouseLeave={handleMouseLeave}
                        className="relative inline-block"
                    >
        <span
            className={`bg-blue-200 rounded-full px-3 py-1 text-sm font-semibold text-blue-700 mr-2 ${feedback === true ? 'bg-green-200' : feedback === false ? 'bg-red-200' : ''}`}>
          {tag}
        </span>
                      {session && hoveredTag === tag && (
                          <div
                              className="absolute -bottom-8 left-1/2 transform -translate-x-1/2 flex gap-2"
                              onMouseEnter={() => handleMouseEnter(tag)}
                              style={{bottom: '-15px'}} // Adjust as needed
                          >
                            <button
                                className={`bg-green-200 p-1 rounded-full ${feedback === true ? 'opacity-50' : ''}`}
                                onClick={() => feedback !== true && sendTagFeedback(tag, true)}
                                disabled={feedback === true}
                            >
                              <HandThumbUpIcon
                                  className={`h-3.5 w-3.5 ${feedback === true ? 'text-black' : 'text-green-700'}`}
                              />
                            </button>
                            <button
                                className={`bg-red-200 p-1 rounded-full ${feedback === false ? 'opacity-50' : ''}`}
                                onClick={() => {
                                  if (feedback !== false) {
                                    sendTagFeedback(tag, false);
                                    setAutoTagsFeedback(prev => ({...prev, [tag]: false}));
                                  }
                                }}
                                disabled={feedback === false}
                            >
                              <HandThumbDownIcon
                                  className={`h-3.5 w-3.5 ${feedback === false ? 'text-black' : 'text-red-700'}`}
                              />
                            </button>
                          </div>
                      )}
                    </div>
                );
              })}
            </div>
            <div className="flex flex-wrap gap-2 mb-4">
              {image &&
                  Array.isArray(image.user_tags) &&
                  image.user_tags.map((tag, index) => (
                      <div key={index} className="relative inline-block group">
            <span
                className="inline-block bg-green-200 rounded-full px-3 py-1 text-sm font-semibold text-green-700 mr-2"
            >
              {tag}
            </span>
                        {session && (
                            <XCircleIcon
                                className="absolute right-0 top-0 h-4 w-4 text-red-500 cursor-pointer opacity-0 group-hover:opacity-100"
                                onClick={() => handleRemoveTag(tag)}
                            />
                        )}
                      </div>
                  ))}
            </div>
            {session && (
                <div className="flex items-center">
                  <input
                      type="text"
                      className="rounded border bg-gray-900 text-white px-3 py-1 text-sm shadow-md"
                      value={newTag}
                      onChange={(e) => setNewTag(e.target.value)}
                  />
                  <button
                      className="inline-flex items-center bg-blue-200 rounded-full px-3 py-1 text-sm font-semibold text-blue-700 ml-2 hover:bg-blue-300 transition-colors duration-200 ease-in-out"
                      onClick={handleAddTag}
                  >
                    <PlusIcon className="h-5 w-5"/>
                  </button>
                </div>
            )}
          </div>
        </div>
        <div className="mt-20">
          <h2 className="text-3xl">
            Similar Images
          </h2>
          <div className="grid grid-cols-5 gap-6">
            {isSimilarImagesLoading ? (
                <Loading/>
            ) : (
                similarImages.map((image, index) => (
                    <Link key={index} href={`/gallery/${image._id}`} passHref>
                      <div className="w-48 h-48 relative overflow-hidden">
                        <Image
                            src={image.thumbnail_url}
                            layout="fill"
                            objectFit="cover"
                            alt={`Similar image ${index + 1}`}
                        />
                      </div>
                    </Link>
                ))
            )}
          </div>
        </div>
      </main>

  );
}