<template>
  <div class="message-container">
    <div class="header">
      <div class="search-bar">
        <input v-model="searchQuery.username" type="text"
          :placeholder="receiver !== '' ? receiver : 'Search username....'" class="search-input"
          @keyup.enter="search" />
      </div>
      <div class="logout-button">
        <button @click="navigateToLogin" class="logout-btn">
          Logout
        </button>
      </div>
    </div>

    <div class="d-flex flex-column messages">
      <div v-for="(msg, index) in messages" :key="index" class="message-box" :class="{
        'sent': msg.author_username === formGet.username,
        'received': msg.receiver_username !== formGet.username
      }">
        <p class="message-content text-black">{{ msg.message }}</p>
        <p class="message-author text-black">{{ msg.author_username }}</p>
      </div>
    </div>

    <div class="footer">
      <div class="footer-input">
        <input v-model="formPush.message" type="text" placeholder="Type a message..." class="footer-input-field"
          @keyup.enter="submit" />
      </div>
      <div class="footer-button">
        <button @click="submit" class="send-btn">Send</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onUnmounted, onMounted, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import API from '@/services/api';
import UserData from '@/components/Scripts/UserData';

type Message = {
  author_id: any,
  receiver_id: any,
  author_username: string,
  receiver_username: string,
  message: string[0],
  timeSent: Date,
}
let intervalId: ReturnType<typeof setInterval>;

const userData = UserData.userDataString;
const router = useRouter();
const messageContainer = ref<HTMLElement | null>(null);

const searchQuery = reactive({
  username: '' as string
});

const receiver = ref('');

const formPush = reactive({
  message: '',
  author_id: '',
  receiver_id: '',
});

const formGet = reactive({
  author_id: null,
  username: '' as string,
  receiver_id: null,
});

const messages = ref<Message[]>([])

const search = async () => {
  const response = await API.post('user/', searchQuery)
  if (response.status === 200) {
    formGet.receiver_id = formPush.receiver_id = response.data.users.id;
    receiver.value = response.data.users.username
    searchQuery.username = ''

    await retrieve()
  }
}

const retrieve = async () => {
  if (userData) {
    const user = JSON.parse(userData);
    formGet.author_id = formPush.author_id = user.userId
    formGet.username = user.username

    const response = await API.post('message/', formGet)
    if (response.status === 200) {
      messages.value = response.data.messages.map(msg => ({
        ...msg, // Copy all properties from the original message
        message: msg.message[0],
        timeSent: new Date(msg.timeSent),
      }));
    }
  }
}

const submit = async () => {
  if (!formPush.message.trim()) {
    alert('Message cannot be empty!');
    return;
  }
  const response = await API.post('send/', formPush)
  if (response) {
    formPush.message = '';
    scrollToBottom();
  }

};

const navigateToLogin = () => {
  router.push({ name: 'login' });
};

const scrollToBottom = () => {
  nextTick(() => {
    if (messageContainer.value) {
      messageContainer.value.scrollTop = messageContainer.value.scrollHeight;
    }
  });
};

onMounted(() => {
  scrollToBottom();
})

onMounted(() => {
  retrieve(); // Initial fetch
  intervalId = setInterval(retrieve, 20000); // Fetch every 5 seconds
});

// Cleanup on unmount
onUnmounted(() => {
  if (intervalId) {
    clearInterval(intervalId);
  }
});
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: Arial, sans-serif;
}

.message-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100%;
}

.header {
  background: #075E54;
  padding: 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: white;
}

.search-bar {
  flex-grow: 1;
  max-width: 300px;
  margin-right: 10px;
}

.search-input {
  width: 100%;
  padding: 10px;
  border-radius: 20px;
  border: none;
  background-color: #128C7E;
  color: white;
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.7);
}

.logout-button .logout-btn {
  padding: 10px 20px;
  background-color: #128C7E;
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
}

.logout-button .logout-btn:hover {
  background-color: #0E7A6D;
}

.background-section {
  flex-grow: 1;
  padding: 20px;
  overflow-y: auto;
  background-color: #ECE5DD;
}

.messages {
  min-height: 50vh;
  background-color: #DCF8C6;
}

.message-box {
  max-width: 40%;
  padding: 10px 15px;
  margin-bottom: 10px;
  border-radius: 15px;
  position: relative;
  background-color: white;
}

.sent {
  align-self: flex-end;
  
}

.message-content {
  margin-bottom: 5px;
}

.message-author {
  font-size: 0.8em;
  color: #888;
}

.footer {
  background-color: #F0F0F0;
  padding: 15px;
  display: flex;
  align-items: center;
}

.footer-input {
  flex-grow: 1;
  margin-right: 10px;
}

.footer-input-field {
  width: 100%;
  padding: 10px;
  border-radius: 20px;
  border: none;
  background-color: white;
}

.footer-button .send-btn {
  padding: 10px 20px;
  background-color: #128C7E;
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
}

.footer-button .send-btn:hover {
  background-color: #0E7A6D;
}

@media (max-width: 768px) {
  .header {
    flex-direction: column;
    align-items: stretch;
  }

  .search-bar {
    max-width: none;
    margin-right: 0;
    margin-bottom: 10px;
  }

  .logout-button {
    text-align: center;
  }

  .message-box {
    max-width: 85%;
  }
}
</style>