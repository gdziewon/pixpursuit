"use client";

import { useState } from "react";
import axios from "axios";

/**
 * Register component
 * This component is responsible for handling user registration.
 * It validates the user's input and sends a POST request to the server to create a new user.
 */
export default function Register() {
  const [email, setEmail] = useState(""); // The user's email
  const [password, setPassword] = useState(""); // The user's password
  const [confirmPassword, setConfirmPassword] = useState(""); // The user's confirmed password
  const [loading, setLoading] = useState(false); // Loading state
  const [message, setMessage] = useState(""); // Message to display

  /**
   * validateEmail function
   * This function validates the user's email using a regular expression.
   *
   * @param {string} email - The user's email.
   * @returns {boolean} - Whether the email is valid.
   */
  const validateEmail = (email) => {
    const emailRegex =
      /[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/;
    return emailRegex.test(email);
  };

  /**
   * validatePassword function
   * This function validates the user's password using a regular expression.
   *
   * @param {string} password - The user's password.
   * @returns {boolean} - Whether the password is valid.
   */
  const validatePassword = (password) => {
    const passwordRegex =
      /(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#\$%\^&\*])(?=.{8,})/;
    return passwordRegex.test(password);
  };

  /**
   * handleSubmit function
   * This function handles the form submission.
   * It validates the user's input and sends a POST request to the server to create a new user.
   *
   * @param {Object} event - The form event.
   */
  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setMessage("");

    if (!validateEmail(email)) {
      setMessage("Invalid email format");
      setLoading(false);
      return;
    }

    if (!validatePassword(password)) {
      setMessage(
        "Password must be at least 8 characters, contain 1 uppercase letter, 1 lowercase letter, 1 number, and 1 special character"
      );
      setLoading(false);
      return;
    }

    if (password !== confirmPassword) {
      setMessage("Passwords do not match");
      setLoading(false);
      return;
    }

    try {
      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/register`,
        {
          email,
          password,
        }
      );
      setMessage(response.data.message);
      setEmail("");
      setPassword("");
      setConfirmPassword("");
    } catch (error) {
      if (error.response) {
        setMessage(error.response.data.detail);
      } else if (error.request) {
        setMessage("An error occurred, please try again");
      } else {
        setMessage("An error occurred");
      }
    } finally {
      setLoading(false);
    }
  };

  // Render the registration form
  return (
    <div className="bg-gray-900 text-white w-full max-w-md mx-auto mt-8 rounded-lg p-4">
      <h1 className="text-3xl font-bold text-gray-200 text-center mb-8">
        PixPursuit
      </h1>
      <form onSubmit={handleSubmit}>
        <div className="bg-gray-800 rounded-md shadow-md p-4">
          <h2 className="text-xl font-semibold text-center mb-4">
            Create account
          </h2>

          <div className="mb-4">
            <label htmlFor="email" className="block text-sm font-medium p-2">
              Email:
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="example.email@example.org"
              className="block w-full px-3 py-2 rounded-md border border-gray-700 bg-gray-700 text-dark focus:outline-none focus:ring-blue-500 focus:ring-2"
            />
          </div>

          <div className="mb-4">
            <label htmlFor="password" className="block text-sm font-medium p-2">
              Password:
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="******"
              className="block w-full px-3 py-2 rounded-md border border-gray-700 bg-gray-700 text-dark focus:outline-none focus:ring-blue-500 focus:ring-2"
            />
          </div>

          <div className="mb-4">
            <label
              htmlFor="confirmPassword"
              className="block text-sm font-medium p-2"
            >
              Confirm Password:
            </label>
            <input
              id="confirmPassword"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              placeholder="******"
              className="block w-full px-3 py-2 rounded-md border border-gray-700 bg-gray-700 text-dark focus:outline-none focus:ring-blue-500 focus:ring-2"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full inline-flex items-center justify-center px-4 py-4 rounded-md text-sm font-bold text-white bg-blue-800 hover:bg-blue-900 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            {loading ? "Registering..." : "Register"}
          </button>
        </div>
      </form>
      {message && <p className="text-red-500 text-sm">{message}</p>}
    </div>
  );
}
