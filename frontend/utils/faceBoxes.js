import axios from "axios";
import Image from "next/image";
import {useState} from "react";

export const BoxOverlay = ({image, boxes, originalSize, session}) => {
    const displayWidth = 800;  // Adjust as needed
    const displayHeight = 800; // Adjust as needed

    const [editableBoxIndex, setEditableBoxIndex] = useState(null);
    const [boxText, setBoxText] = useState('');
    const [isMouseOver, setIsMouseOver] = useState(false);
    const isLoggedIn = session && session.accessToken;

    const scaleX = originalSize.width ? displayWidth / originalSize.width : 1;
    const scaleY = originalSize.height ? displayHeight / originalSize.height : 1;
    const scale = Math.min(scaleX, scaleY) * (0.47 * (originalSize.height / originalSize.width) + 0.42);

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
                                    top: '102%',
                                    left: '0',
                                    right: '0',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    width: '100%',
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
                                        width: 'auto',
                                        minWidth: '100px',
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