"use client";

import { useState, useEffect } from "react";
import Image from "next/image";
import { PlusIcon, PencilIcon, XMarkIcon, CheckIcon, HandThumbDownIcon, HandThumbUpIcon} from "@heroicons/react/24/solid";
import getSingleImage from "@/utils/getSingleImage";
import Loading from "@/app/loading";
import axios from 'axios';
import {useSession} from "next-auth/react";

export default function ImagePage({ params }) {
  const [image, setImage] = useState(null);
  const [newTag, setNewTag] = useState(null);
  const [editingDescription, setEditingDescription] = useState(false);
  const [editedDescription, setEditedDescription] = useState("");
  const { data: session } = useSession();
  const [hoveredTag, setHoveredTag] = useState(null);
  const [leaveTimer, setLeaveTimer] = useState(null);
  const [originalSize, setOriginalSize] = useState({ width: 0, height: 0 });
  const id = params.id;

  useEffect(() => {
    const fetchImage = async () => {
      const imageData = await getSingleImage(id);
      setImage(imageData);
      setEditedDescription(imageData.description);
      const img = new window.Image();
      img.onload = () => {
        setOriginalSize({ width: img.naturalWidth, height: img.naturalHeight });
      };
      img.src = imageData.image_url;
    };

    fetchImage();
  }, [id]);

  // Function to handle adding user-defined tags
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
        // You might want to update the UI or state based on the feedback
      } else {
        alert("Failed to submit feedback");
      }
    } catch (error) {
      console.error("Error submitting feedback:", error);
      alert("Error submitting feedback");
    }
  };

  const checkFeedbackHistory = (tag) => {
    if (!session || !image.feedback_history || !image.feedback_history[session.user.name]) {
      return null;
    }

    const userFeedback = image.feedback_history[session.user.name];
    return userFeedback[tag];
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
    <main className="flex p-6">
      <div className="w-1/2">
        <div className="flex justify-center flex-col">
          <BoxOverlay image={image} boxes={image.embeddings_box || []} originalSize={originalSize} session={session}/>
        </div>
          <p className="">Taken: {image.metadata.DateTime}</p>
          <p>Added by: {image.added_by}</p>
      </div>
      <div className="w-1/2 pl-6">
        <h1 className="text-3xl font-bold text-teal-100 dark:text-white mb-4">
          Photo description:
        </h1>
        {editingDescription ? (
            <div>
              <div>
      <textarea
          className="w-full rounded border bg-gray-900 text-white px-3 py-1 text-lg shadow-md" // Adjusted for visibility
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
        ) : (
            <div>
              <h1 className="text-2xl text-gray-900 dark:text-white mb-4" style={{color: 'white'}}>
                {image.description}
              </h1>
              {session && (
                  <button
                      className="inline-flex items-center bg-gray-200 rounded-full px-3 py-1 text-sm font-semibold text-gray-800 ml-2 hover:bg-gray-400 transition-colors duration-200 ease-in-out"
                      onClick={toggleEditingDescription}
                  >
                    <PencilIcon className="h-5 w-5 mr-2"/> Edit Description
                  </button>
              )}
            </div>
        )}
        <h1 className="text-3xl font-bold text-teal-100 dark:text-white mb-4">
          Tags:
        </h1>

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
        <span className="bg-blue-200 rounded-full px-3 py-1 text-sm font-semibold text-blue-700 mr-2">
          {tag}
        </span>
                  {session && hoveredTag === tag && (
                      <div className="absolute -bottom-8 left-0 flex gap-2" onMouseEnter={() => handleMouseEnter(tag)}>
                        <button
                            className={`bg-green-200 p-1 rounded-full ${feedback === true ? 'opacity-50' : ''}`}
                            onClick={() => feedback !== true && sendTagFeedback(tag, true)}
                            disabled={feedback === true}
                        >
                          <HandThumbUpIcon
                              className={`h-4 w-4 ${feedback === true ? 'text-black' : 'text-green-700'}`}/>
                        </button>
                        <button
                            className={`bg-red-200 p-1 rounded-full ${feedback === false ? 'opacity-50' : ''}`}
                            onClick={() => feedback !== false && sendTagFeedback(tag, false)}
                            disabled={feedback === false}
                        >
                          <HandThumbDownIcon
                              className={`h-4 w-4 ${feedback === false ? 'text-black' : 'text-red-700'}`}/>
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
                  <span
                      key={index}
                      className="inline-block bg-green-200 rounded-full px-3 py-1 text-sm font-semibold text-green-700 mr-2"
                  >
                {tag}
              </span>
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
    </main>
  );
}

const BoxOverlay = ({ image, boxes, originalSize, session }) => {
  const displayWidth = 800;  // Adjust as needed
  const displayHeight = 800; // Adjust as needed

  const [editableBoxIndex, setEditableBoxIndex] = useState(null);
  const [boxText, setBoxText] = useState('');
  const [isMouseOver, setIsMouseOver] = useState(false);
  const isLoggedIn = session && session.accessToken;

  const scaleX = originalSize.width ? displayWidth / originalSize.width : 1;
  const scaleY = originalSize.height ? displayHeight / originalSize.height : 1;
  const scale = Math.min(scaleX, scaleY) * (0.415 * (originalSize.height / originalSize.width) + 0.436);

  const handleBoxClick = (index, e) => {
    e.stopPropagation();  // Prevents event bubbling up
    setEditableBoxIndex(index);
    const userFaceAtIndex = image.user_faces[index];
    setBoxText(userFaceAtIndex);
  };

  const handleBoxTextChange = (e) => {
    setBoxText(e.target.value);
  };

  const handlePlusButtonClick = async (e, index) => {
    e.stopPropagation();
    console.log('plus button clicked');
    if (boxText.trim() === '') {
      console.log('No name entered.');
      return;
    }

    try {
      const faceData = {
        inserted_id: image._id,
        anonymous_index: index,
        name: boxText,
      };

      const response = await axios.post('http://localhost:8000/add-user-face', faceData, {
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${session.accessToken}`,
        },
      });

      if (response.status === 200) {
        alert('Name added successfully');
        // Update state or UI as needed
      } else {
        alert('Failed to add name to face');
      }
    } catch (error) {
      alert('Error adding name to face:', error);
    }

    setEditableBoxIndex(null);
  };

  const handleMouseDownOnPlusButton = (event) => {
    event.preventDefault();
  };

  return (
      <div style={{ position: 'relative' }}
           onMouseEnter={() => setIsMouseOver(true)}
           onMouseLeave={() => setIsMouseOver(false)}>
        <Image
            src={image.image_url}
            alt={image.description}
            width={displayWidth}
            height={displayHeight}
            quality={100}
            className="rounded-lg"
        />
        {isMouseOver &&
        boxes.map((box, index) => (
            <div
                key={index}
                style={{
                  position: 'absolute',
                  border: '2px solid red',
                  left: `${box[0] * scale}px`,
                  top: `${box[1] * scale}px`,
                  width: `${(box[2] - box[0]) * scale}px`,
                  height: `${(box[3] - box[1]) * scale}px`,
                  cursor: 'pointer',
                }}
                onClick={(e) => handleBoxClick(index, e)}
            >
              {editableBoxIndex === index && (
                  <div
                      style={{
                        position: 'absolute',
                        top: '100%',
                        left: '0',
                        right: '0',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                      }}
                  >
                    <input
                        className="inline-block bg-blue-200 rounded-s-lg px-3 py-1 text-sm font-semibold text-gray-950 mr-2"
                        type="text"
                        value={boxText}
                        onChange={isLoggedIn ? handleBoxTextChange : undefined} // Only allow change if logged in
                        readOnly={!isLoggedIn}
                        onBlur={() => setEditableBoxIndex(null)}
                        autoFocus
                        style={{
                          flexGrow: 1,
                          marginRight: '2px',
                          border: '1px solid',
                        }}
                    />
                    {isLoggedIn && (
                    <button
                        className="inline-block bg-blue-200 rounded-e-lg px-3 py-1 text-sm font-semibold text-gray-950 mr-2"
                        onMouseDown={handleMouseDownOnPlusButton}
                        onClick={(e) => handlePlusButtonClick(e, index)}
                        style={{
                          border: '1px solid',
                          flexShrink: 0,
                        }}
                    >
                      +
                    </button>
                        )}
                  </div>
              )}
            </div>
        ))}
      </div>
  );
};
