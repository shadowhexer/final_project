<template>
  <div class="min-h-screen bg-gray-100">
    <!-- Navbar -->
    <div class="bg-white shadow-md py-4 px-8 flex justify-between items-center">
      <!-- Left Side - Title -->
      <div class="text-2xl font-bold text-gray-700">Dashboard</div>
      
      <!-- Right Side - Buttons -->
      <div class="flex space-x-4">
        <!-- About Button -->
        <button class="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 transition duration-300">About</button>
        
        <!-- Messages Button -->
        <button class="bg-green-500 text-white px-4 py-2 rounded-md hover:bg-green-600 transition duration-300">Messages</button>
        
        <!-- Profile Dropdown Button -->
        <div class="relative">
          <button class="bg-gray-700 text-white px-4 py-2 rounded-md hover:bg-gray-800 transition duration-300">
            Profile
          </button>
          <div class="absolute right-0 w-48 mt-2 bg-white shadow-lg rounded-md hidden group-hover:block">
            <ul class="py-2">
              <li class="px-4 py-2 hover:bg-gray-100 cursor-pointer">View Profile</li>
              <li class="px-4 py-2 hover:bg-gray-100 cursor-pointer">Edit Profile</li>
              <li class="px-4 py-2 hover:bg-gray-100 cursor-pointer">Logout</li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- Dashboard Section -->
    <div class="px-8 py-10">
      <h1 class="text-3xl font-bold text-gray-700">Welcome, User!</h1>
      <p class="text-lg text-gray-500 mt-4">You have successfully logged in. Explore your dashboard.</p>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'Dashboard',
});
</script>

<style scoped>
/* Dropdown Hover */
button:hover + .absolute {
  display: block;
}

.group:hover .hidden {
  display: block;
}
</style>
