import React from "react";
import "./AccountSettingsPage.css";

const AccountSettingsPage = () => {
  return (
    <div className="account-settings-container">
      <div className="settings-content">
        <button className="back-btn" onClick={() => window.history.back()}>
          Back
        </button>
        <h1>Account Settings</h1>

        <div className="settings-section">
          <h2>Change Password</h2>
          <input type="password" placeholder="Current Password" />
          <input type="password" placeholder="New Password" />
          <input type="password" placeholder="Confirm New Password" />
          <div className="actions">
            <button className="update-btn">Update Password</button>
          </div>
        </div>

        <div className="settings-section">
          <h2>Personal Information</h2>
          <input type="text" placeholder="Name" />
          <textarea rows="3" placeholder="Biography" />
          <input type="text" placeholder="Interests" />
          <div className="actions">
            <button className="update-btn">Update Information</button>
          </div>
        </div>

        <div className="settings-section">
          <h2>Notification Preferences</h2>
          <div className="checkbox-group">
            <label>
              <input type="checkbox" /> <span>New Matches</span>
            </label>
            <label>
              <input type="checkbox" /> <span>Messages</span>
            </label>
            <label>
              <input type="checkbox" /> <span>Profile Updates</span>
            </label>
          </div>
          <div className="actions">
            <button className="update-btn">Save Preferences</button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AccountSettingsPage;
