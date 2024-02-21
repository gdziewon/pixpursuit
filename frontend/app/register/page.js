"use client";

import { useState } from "react";
import axios from "axios";

export default function Register() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const validateEmail = (email) => {
    const emailRegex =
      /[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/;
    return emailRegex.test(email);
  };

  const validatePassword = (password) => {
    const passwordRegex =
      /(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#\$%\^&\*])(?=.{8,})/;
    return passwordRegex.test(password);
  };
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
      <p className="text-sm mt-4 text-gray-500">
        Already have an account?{" "}
        <a
          href="/login"
          className="text-blue-500 hover:text-blue-700 font-medium"
        >
          Log in
        </a>
      </p>
    </div>
  );
}
