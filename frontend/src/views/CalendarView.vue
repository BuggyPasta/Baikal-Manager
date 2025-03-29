# Create the CalendarView component
<template>
  <div class="container mx-auto px-4 py-8">
    <!-- Calendar Header -->
    <div class="flex flex-col md:flex-row justify-between items-center mb-8">
      <div class="flex items-center space-x-4 mb-4 md:mb-0">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Calendar</h1>
        <div class="flex items-center bg-white dark:bg-gray-800 rounded-lg shadow">
          <button
            v-for="view in views"
            :key="view.value"
            @click="currentView = view.value"
            :class="[
              'px-4 py-2 text-sm font-medium',
              currentView === view.value
                ? 'bg-blue-600 text-white'
                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
            ]"
          >
            {{ view.label }}
          </button>
        </div>
      </div>
      
      <div class="flex items-center space-x-4">
        <button
          @click="navigateDate('prev')"
          class="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        
        <button
          @click="currentDate = new Date()"
          class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
        >
          Today
        </button>
        
        <span class="text-lg font-semibold text-gray-900 dark:text-white">
          {{ formatDateRange }}
        </span>
        
        <button
          @click="navigateDate('next')"
          class="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center h-96">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 dark:bg-red-900 p-4 rounded-lg mb-8">
      <p class="text-red-800 dark:text-red-200">{{ error }}</p>
      <button
        @click="fetchEvents"
        class="mt-2 text-sm text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-200"
      >
        Try again
      </button>
    </div>

    <!-- Calendar Grid -->
    <div v-else class="bg-white dark:bg-gray-800 rounded-lg shadow">
      <!-- Month View -->
      <div v-if="currentView === 'month'" class="grid grid-cols-7 gap-px">
        <!-- Day Headers -->
        <div
          v-for="day in weekDays"
          :key="day"
          class="p-2 text-center text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-50 dark:bg-gray-700"
        >
          {{ day }}
        </div>
        
        <!-- Calendar Days -->
        <div
          v-for="(day, index) in monthDays"
          :key="index"
          :class="[
            'min-h-[120px] p-2',
            day.isCurrentMonth ? 'bg-white dark:bg-gray-800' : 'bg-gray-50 dark:bg-gray-700',
            day.isToday ? 'border-2 border-blue-600' : ''
          ]"
        >
          <div class="flex justify-between items-center mb-1">
            <span
              :class="[
                'text-sm font-medium',
                day.isCurrentMonth
                  ? 'text-gray-900 dark:text-white'
                  : 'text-gray-400 dark:text-gray-500'
              ]"
            >
              {{ day.date.getDate() }}
            </span>
            <button
              v-if="day.isCurrentMonth"
              @click="openNewEventModal(day.date)"
              class="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
            </button>
          </div>
          
          <!-- Events -->
          <div class="space-y-1">
            <div
              v-for="event in day.events"
              :key="event.id"
              @click="openEventModal(event)"
              class="px-2 py-1 text-xs rounded-md cursor-pointer truncate"
              :class="[
                event.color ? `bg-${event.color}-100 text-${event.color}-800` : 'bg-blue-100 text-blue-800',
                `dark:bg-${event.color || 'blue'}-800 dark:text-${event.color || 'blue'}-100`
              ]"
            >
              {{ event.title }}
            </div>
          </div>
        </div>
      </div>

      <!-- Week View -->
      <div v-else-if="currentView === 'week'" class="grid grid-cols-8 gap-px">
        <!-- Time Column -->
        <div class="bg-gray-50 dark:bg-gray-700">
          <div class="h-12"></div> <!-- Header spacer -->
          <div
            v-for="hour in 24"
            :key="hour"
            class="h-12 border-t border-gray-200 dark:border-gray-600 px-2 py-1"
          >
            <span class="text-xs text-gray-500 dark:text-gray-400">
              {{ formatHour(hour - 1) }}
            </span>
          </div>
        </div>

        <!-- Days Columns -->
        <div
          v-for="day in weekDays"
          :key="day"
          class="relative"
        >
          <!-- Day Header -->
          <div
            class="h-12 px-2 py-1 text-center text-sm font-medium bg-gray-50 dark:bg-gray-700 text-gray-700 dark:text-gray-300"
          >
            {{ day }}
          </div>

          <!-- Hours Grid -->
          <div class="relative">
            <div
              v-for="hour in 24"
              :key="hour"
              class="h-12 border-t border-gray-200 dark:border-gray-600"
            ></div>

            <!-- Events -->
            <div
              v-for="event in getEventsForDay(day)"
              :key="event.id"
              :style="{
                top: `${getEventTop(event)}px`,
                height: `${getEventHeight(event)}px`,
                left: '4px',
                right: '4px'
              }"
              @click="openEventModal(event)"
              class="absolute px-2 py-1 text-xs rounded-md cursor-pointer overflow-hidden"
              :class="[
                event.color ? `bg-${event.color}-100 text-${event.color}-800` : 'bg-blue-100 text-blue-800',
                `dark:bg-${event.color || 'blue'}-800 dark:text-${event.color || 'blue'}-100`
              ]"
            >
              {{ event.title }}
            </div>
          </div>
        </div>
      </div>

      <!-- Day View -->
      <div v-else class="grid grid-cols-1">
        <!-- Time Column -->
        <div class="relative">
          <div
            v-for="hour in 24"
            :key="hour"
            class="h-16 border-t border-gray-200 dark:border-gray-600"
          >
            <span class="absolute -mt-3 ml-2 text-xs text-gray-500 dark:text-gray-400">
              {{ formatHour(hour - 1) }}
            </span>
          </div>

          <!-- Events -->
          <div
            v-for="event in dayEvents"
            :key="event.id"
            :style="{
              top: `${getEventTop(event)}px`,
              height: `${getEventHeight(event)}px`,
              left: '60px',
              right: '4px'
            }"
            @click="openEventModal(event)"
            class="absolute px-4 py-2 rounded-lg cursor-pointer"
            :class="[
              event.color ? `bg-${event.color}-100 text-${event.color}-800` : 'bg-blue-100 text-blue-800',
              `dark:bg-${event.color || 'blue'}-800 dark:text-${event.color || 'blue'}-100`
            ]"
          >
            <div class="font-medium">{{ event.title }}</div>
            <div class="text-xs">{{ formatEventTime(event) }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- New Event Button -->
    <button
      @click="openNewEventModal()"
      class="fixed bottom-8 right-8 bg-blue-600 text-white rounded-full p-4 shadow-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
    >
      <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
      </svg>
    </button>

    <!-- Event Modal -->
    <EventModal
      v-if="showEventModal"
      :event="selectedEvent"
      :date="selectedDate"
      @close="closeEventModal"
      @save="saveEvent"
      @delete="deleteEvent"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { format, addDays, startOfWeek, endOfWeek, startOfMonth, endOfMonth, eachDayOfInterval, isSameMonth, isToday } from 'date-fns'
import EventModal from '@/components/EventModal.vue'

// View options
const views = [
  { label: 'Month', value: 'month' },
  { label: 'Week', value: 'week' },
  { label: 'Day', value: 'day' }
]

// State
const currentView = ref('month')
const currentDate = ref(new Date())
const events = ref([])
const loading = ref(false)
const error = ref(null)
const showEventModal = ref(false)
const selectedEvent = ref(null)
const selectedDate = ref(null)

// Week days array
const weekDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

// Computed properties
const formatDateRange = computed(() => {
  if (currentView.value === 'month') {
    return format(currentDate.value, 'MMMM yyyy')
  } else if (currentView.value === 'week') {
    const start = startOfWeek(currentDate.value)
    const end = endOfWeek(currentDate.value)
    return `${format(start, 'MMM d')} - ${format(end, 'MMM d, yyyy')}`
  } else {
    return format(currentDate.value, 'EEEE, MMMM d, yyyy')
  }
})

const monthDays = computed(() => {
  const start = startOfMonth(currentDate.value)
  const end = endOfMonth(currentDate.value)
  const days = eachDayOfInterval({ start, end })
  
  return days.map(date => ({
    date,
    isCurrentMonth: isSameMonth(date, currentDate.value),
    isToday: isToday(date),
    events: getEventsForDate(date)
  }))
})

const dayEvents = computed(() => {
  return getEventsForDate(currentDate.value)
})

// Methods
function navigateDate(direction) {
  const amount = direction === 'next' ? 1 : -1
  if (currentView.value === 'month') {
    currentDate.value = new Date(currentDate.value.setMonth(currentDate.value.getMonth() + amount))
  } else if (currentView.value === 'week') {
    currentDate.value = addDays(currentDate.value, amount * 7)
  } else {
    currentDate.value = addDays(currentDate.value, amount)
  }
}

function formatHour(hour) {
  return format(new Date().setHours(hour, 0, 0, 0), 'h a')
}

function formatEventTime(event) {
  return `${format(new Date(event.start), 'h:mm a')} - ${format(new Date(event.end), 'h:mm a')}`
}

function getEventsForDate(date) {
  // Filter events for the given date
  return events.value.filter(event => {
    const eventDate = new Date(event.start)
    return (
      eventDate.getFullYear() === date.getFullYear() &&
      eventDate.getMonth() === date.getMonth() &&
      eventDate.getDate() === date.getDate()
    )
  })
}

function getEventTop(event) {
  const start = new Date(event.start)
  return (start.getHours() * 60 + start.getMinutes()) * (48/60) // 48px per hour
}

function getEventHeight(event) {
  const start = new Date(event.start)
  const end = new Date(event.end)
  const minutes = (end - start) / 1000 / 60
  return minutes * (48/60) // 48px per hour
}

function openNewEventModal(date = null) {
  selectedEvent.value = null
  selectedDate.value = date || currentDate.value
  showEventModal.value = true
}

function openEventModal(event) {
  selectedEvent.value = event
  selectedDate.value = new Date(event.start)
  showEventModal.value = true
}

function closeEventModal() {
  showEventModal.value = false
  selectedEvent.value = null
  selectedDate.value = null
}

async function fetchEvents() {
  loading.value = true
  error.value = null
  try {
    // TODO: Implement API call to fetch events
    // For now, using placeholder data
    events.value = []
  } catch (err) {
    error.value = 'Failed to load events. Please try again.'
    console.error('Error fetching events:', err)
  } finally {
    loading.value = false
  }
}

async function saveEvent(eventData) {
  try {
    if (selectedEvent.value) {
      // TODO: Implement update event API call
      const index = events.value.findIndex(e => e.id === selectedEvent.value.id)
      if (index !== -1) {
        events.value[index] = { ...eventData, id: selectedEvent.value.id }
      }
    } else {
      // TODO: Implement create event API call
      events.value.push({ ...eventData, id: Date.now() })
    }
    closeEventModal()
  } catch (err) {
    console.error('Error saving event:', err)
    // TODO: Show error message to user
  }
}

async function deleteEvent(eventId) {
  try {
    // TODO: Implement delete event API call
    events.value = events.value.filter(e => e.id !== eventId)
    closeEventModal()
  } catch (err) {
    console.error('Error deleting event:', err)
    // TODO: Show error message to user
  }
}

// Watch for view/date changes to refresh events
watch([currentView, currentDate], () => {
  fetchEvents()
})

// Initial load
onMounted(() => {
  fetchEvents()
})
</script> 