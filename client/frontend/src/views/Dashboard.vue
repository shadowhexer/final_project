<template>
  <v-container class="min-h-screen bg-gray-100">
    <!-- Navbar -->
    <v-row class="navbar">
      <!-- Left Side - Title (Dashboard) -->
      <v-col cols="auto">
        <div class="navbar-title">Dashboard</div>
      </v-col>

      <!-- Right Side - Buttons -->
      <v-col cols="auto" class="navbar-buttons">
        <v-btn class="navbar-btn" @click="navigateToMessages">Messages</v-btn>
        <v-btn class="navbar-btn" color="error" @click="logout">
          Logout
        </v-btn>
      </v-col>
    </v-row>

    <!-- Dashboard Section -->
    <v-row class="dashboard-section">
      <v-col>
        <h1 class="welcome-title">Welcome, {{ user }}!</h1>
        <p class="welcome-description">You have successfully logged in. Explore your dashboard.</p>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import UserData from '../components/Scripts/UserData';

const userData = UserData.userDataString;
const user = ref('')

const menuVisible = ref(false);
const router = useRouter();

const logout = () => {
  sessionStorage.removeItem('userData')
  // Implement logout functionality (e.g., clear session data)
  window.location.href = '/login'; // Example redirect to login
};

const navigateToMessages = () => {
  window.location.href = '/message'; // Navigate to Messages page
};

if (userData) {
  const data = JSON.parse(userData);
  user.value = data.username;
}
</script>

<style scoped>
/* Basic Styles for Navbar */
.navbar {
  background-color: #ffffff;
  padding: 16px 32px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.navbar-title {
  font-size: 24px;
  font-weight: bold;
  color: #4a4a4a;
}

.navbar-buttons {
  display: flex;
  justify-content: flex-end;
  align-items: center;
}

.navbar-btn {
  margin-right: 16px;
  background-color: #1e40af;
  color: white;
  padding: 8px 16px;
  border-radius: 4px;
  transition: background-color 0.3s ease;
}

.navbar-btn:hover {
  background-color: #2563eb;
}

.profile-btn {
  background-color: #6b7280;
  color: white;
  padding: 8px 16px;
  border-radius: 4px;
  transition: background-color 0.3s ease;
}

.profile-btn:hover {
  background-color: #4b5563;
}

/* Styles for Dashboard Section */
.dashboard-section {
  padding: 40px 32px;
}

.welcome-title {
  font-size: 32px;
  font-weight: bold;
  color: #4a4a4a;
}

.welcome-description {
  font-size: 18px;
  color: #6b7280;
  margin-top: 16px;
}
</style>