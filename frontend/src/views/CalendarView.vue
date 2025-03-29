# Create the CalendarView component
<template>
  <div class="container mx-auto px-4 py-8">
    <!-- View Controls -->
    <div class="flex justify-between items-center mb-6">
      <div class="flex items-center space-x-4">
        <button
          v-for="view in ['month', 'week', 'day', 'list']"
          :key="view"
          @click="currentView = view"
          :class="[
            'px-4 py-2 rounded-md text-sm font-medium',
            currentView === view
              ? 'bg-blue-600 text-white'
              : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
          ]"
        >
          {{ view.charAt(0).toUpperCase() + view.slice(1) }}
        </button>
      </div>

      <div v-if="currentView !== 'list'" class="flex items-center space-x-4">
        <button
          class="btn-secondary"
          @click="goToToday"
        >
          Today
        </button>
        <div class="flex items-center space-x-2">
          <button
            class="p-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center justify-center w-8 h-8"
            @click="previousPeriod"
          >
            <span class="sr-only">Previous</span>
            &lt;
          </button>
          <h2 class="text-xl font-semibold">{{ currentPeriodLabel }}</h2>
          <button
            class="p-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center justify-center w-8 h-8"
            @click="nextPeriod"
          >
            <span class="sr-only">Next</span>
            &gt;
          </button>
        </div>
      </div>
    </div>

    <!-- List View -->
    <div v-if="currentView === 'list'" class="bg-white dark:bg-gray-800 rounded-lg shadow">
      <div class="divide-y divide-gray-200 dark:divide-gray-700">
        <div
          v-for="event in sortedEvents"
          :key="event.id"
          @click="openEventModal(event)"
          class="p-4 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer"
        >
          <div class="flex justify-between items-start">
            <div>
              <h3 class="text-lg font-medium text-gray-900 dark:text-white">
                {{ event.title }}
              </h3>
              <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
                {{ formatEventDateTime(event) }}
              </p>
              <p v-if="event.description" class="mt-2 text-sm text-gray-600 dark:text-gray-300">
                {{ event.description }}
              </p>
            </div>
            <div
              :class="[
                'w-3 h-3 rounded-full',
                `bg-${event.color || 'blue'}-500`
              ]"
            ></div>
          </div>
        </div>
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
      <div v-if="currentView === 'month'" class="grid grid-cols-7 gap-0 border border-gray-200 dark:border-gray-700">
        <!-- Day Headers -->
        <div
          v-for="day in weekDays"
          :key="day"
          class="p-2 text-center text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-50 dark:bg-gray-700 border-b border-r border-gray-200 dark:border-gray-700"
        >
          {{ format(day, 'EEE') }}
          <div class="text-xs">{{ format(day, 'd MMM') }}</div>
        </div>
        
        <!-- Calendar Days -->
        <div
          v-for="(day, index) in monthDays"
          :key="index"
          :class="[
            'min-h-[120px] p-2 border-b border-r border-gray-200 dark:border-gray-700',
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
      <div v-else-if="currentView === 'week'" class="calendar-grid grid-cols-8">
        <!-- Time Column -->
        <div class="calendar-header-cell"></div>
        <div
          v-for="day in weekDays"
          :key="format(day, 'yyyy-MM-dd')"
          class="calendar-header-cell"
        >
          {{ format(day, 'EEE, MMM d') }}
        </div>

        <!-- Time slots -->
        <template v-for="hour in 24" :key="hour">
          <div class="calendar-time-cell">
            {{ formatHour(hour - 1) }}
          </div>
          <template v-for="day in weekDays" :key="`${hour}-${format(day, 'yyyy-MM-dd')}`">
            <div class="calendar-week-cell relative">
              <!-- First 30 minutes -->
              <div class="h-[30px] relative border-b border-gray-100 dark:border-gray-700">
                <div
                  v-for="event in getEventsForTimeSlot(day, hour - 1, 0)"
                  :key="event.id"
                  @click="openEventModal(event)"
                  class="absolute inset-x-1 rounded-md px-2 py-1 text-xs cursor-pointer overflow-hidden"
                  :class="getEventClasses(event)"
                  :style="getEventStyles(event)"
                >
                  {{ event.title }}
                </div>
              </div>
              <!-- Second 30 minutes -->
              <div class="h-[30px] relative">
                <div
                  v-for="event in getEventsForTimeSlot(day, hour - 1, 30)"
                  :key="event.id"
                  @click="openEventModal(event)"
                  class="absolute inset-x-1 rounded-md px-2 py-1 text-xs cursor-pointer overflow-hidden"
                  :class="getEventClasses(event)"
                  :style="getEventStyles(event)"
                >
                  {{ event.title }}
                </div>
              </div>
            </div>
          </template>
        </template>
      </div>

      <!-- Day View -->
      <div v-else-if="currentView === 'day'" class="grid grid-cols-[100px_1fr] border border-gray-200 dark:border-gray-700">
        <!-- Header -->
        <div class="calendar-header-cell border-r border-gray-200 dark:border-gray-700">Time</div>
        <div class="calendar-header-cell">
          {{ format(currentDate, 'EEEE, MMM d') }}
        </div>

        <!-- Time slots -->
        <template v-for="hour in 24" :key="hour">
          <!-- First 30 minutes -->
          <div class="calendar-time-cell border-r border-gray-200 dark:border-gray-700">
            {{ formatHour(hour - 1) }}
          </div>
          <div class="calendar-week-cell relative">
            <div class="h-[30px] relative border-b border-gray-100 dark:border-gray-700">
              <div
                v-for="event in getEventsForTimeSlot(currentDate, hour - 1, 0)"
                :key="event.id"
                @click="openEventModal(event)"
                class="absolute inset-x-1 rounded-md px-2 py-1 text-sm cursor-pointer overflow-hidden"
                :class="getEventClasses(event)"
                :style="getEventStyles(event)"
              >
                {{ event.title }}
              </div>
            </div>
            <!-- Second 30 minutes -->
            <div class="h-[30px] relative">
              <div
                v-for="event in getEventsForTimeSlot(currentDate, hour - 1, 30)"
                :key="event.id"
                @click="openEventModal(event)"
                class="absolute inset-x-1 rounded-md px-2 py-1 text-sm cursor-pointer overflow-hidden"
                :class="getEventClasses(event)"
                :style="getEventStyles(event)"
              >
                {{ event.title }}
              </div>
            </div>
          </div>
        </template>
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
import { format, addDays, startOfWeek, endOfWeek, startOfMonth, endOfMonth, eachDayOfInterval, isSameMonth, isToday, parseISO, compareAsc, setMinutes, setHours, addMinutes, isWithinInterval, isBefore, isAfter, differenceInMinutes } from 'date-fns'
import EventModal from '@/components/EventModal.vue'

// View options
const views = ['month', 'week', 'day', 'list']

// State
const currentView = ref('month')
const currentDate = ref(new Date())
const events = ref([])
const loading = ref(false)
const error = ref(null)
const showEventModal = ref(false)
const selectedEvent = ref(null)
const selectedDate = ref(null)

// Week days array for headers
const weekDays = computed(() => {
  const start = startOfWeek(currentDate.value)
  return Array.from({ length: 7 }, (_, i) => addDays(start, i))
})

// Current period label
const currentPeriodLabel = computed(() => {
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
  const date = new Date();
  date.setHours(hour, 0, 0, 0); // Set minutes to 0
  return format(date, 'HH:mm');
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

// Format event date and time for list view
function formatEventDateTime(event) {
  const start = parseISO(event.start)
  const end = parseISO(event.end)
  
  if (event.allDay) {
    return format(start, 'EEEE, d MMMM yyyy')
  }
  
  if (isSameDay(start, end)) {
    return `${format(start, 'EEEE, d MMMM yyyy')} ${format(start, 'HH:mm')} - ${format(end, 'HH:mm')}`
  }
  
  return `${format(start, 'EEEE, d MMMM yyyy HH:mm')} - ${format(end, 'EEEE, d MMMM yyyy HH:mm')}`
}

// Sort events for list view
const sortedEvents = computed(() => {
  const now = new Date()
  return events.value.sort((a, b) => {
    const aStart = parseISO(a.start)
    const bStart = parseISO(b.start)
    const aDistance = Math.abs(aStart - now)
    const bDistance = Math.abs(bStart - now)
    
    if (aStart >= now && bStart >= now) {
      // Both future events - sort by closest to now
      return compareAsc(aStart, bStart)
    } else if (aStart < now && bStart < now) {
      // Both past events - sort by closest to now
      return compareAsc(bDistance, aDistance)
    } else {
      // Mix of past and future - future events first
      return aStart >= now ? -1 : 1
    }
  })
})

// Navigation methods
function goToToday() {
  currentDate.value = new Date()
}

function previousPeriod() {
  if (currentView.value === 'month') {
    currentDate.value = new Date(currentDate.value.setMonth(currentDate.value.getMonth() - 1))
  } else if (currentView.value === 'week') {
    currentDate.value = addDays(currentDate.value, -7)
  } else {
    currentDate.value = addDays(currentDate.value, -1)
  }
}

function nextPeriod() {
  if (currentView.value === 'month') {
    currentDate.value = new Date(currentDate.value.setMonth(currentDate.value.getMonth() + 1))
  } else if (currentView.value === 'week') {
    currentDate.value = addDays(currentDate.value, 7)
  } else {
    currentDate.value = addDays(currentDate.value, 1)
  }
}

// Helper functions for events
function getEventsForTimeSlot(date, hour, minute) {
  const slotStart = setMinutes(setHours(new Date(date), hour), minute)
  const slotEnd = addMinutes(slotStart, 30)
  
  return events.value.filter(event => {
    const eventStart = new Date(event.start)
    const eventEnd = new Date(event.end)
    
    return (
      isWithinInterval(slotStart, { start: eventStart, end: eventEnd }) ||
      isWithinInterval(slotEnd, { start: eventStart, end: eventEnd }) ||
      (isBefore(eventStart, slotStart) && isAfter(eventEnd, slotEnd))
    )
  })
}

function getEventClasses(event) {
  return [
    `bg-${event.color || 'blue'}-100`,
    `text-${event.color || 'blue'}-800`,
    `dark:bg-${event.color || 'blue'}-800`,
    `dark:text-${event.color || 'blue'}-100`
  ]
}

function getEventStyles(event) {
  const start = new Date(event.start)
  const end = new Date(event.end)
  const duration = differenceInMinutes(end, start)
  const top = `${(start.getHours() * 60 + start.getMinutes()) * (100/1440)}%` // percentage through the day
  const height = `${Math.min(duration * (100/1440), 100)}%` // percentage of day, max 100%
  
  return {
    top,
    height,
    zIndex: duration > 30 ? 10 : 1
  }
}

function getMinutesFromMidnight(date) {
  return date.getHours() * 60 + date.getMinutes()
}
</script> 