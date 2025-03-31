# Create the CalendarView component
<template>
  <div class="calendar-view h-full flex flex-col">
    <!-- Calendar Header -->
    <div class="calendar-header">
      <div class="flex items-center justify-between mb-4">
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
          <button
            class="btn-secondary"
            @click="fetchEvents"
            :disabled="loading"
          >
            <svg v-if="loading" class="animate-spin h-5 w-5 mr-2" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Sync
          </button>
          <div class="flex items-center">
            <button @click="previousPeriod" class="p-2 flex items-center justify-center hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full">
              <img :src="arrowPrevious" alt="Previous" class="w-5 h-5 dark:invert" />
            </button>
            <h2 class="text-xl font-semibold px-4 min-w-[200px] text-center">{{ currentPeriodLabel }}</h2>
            <button @click="nextPeriod" class="p-2 flex items-center justify-center hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full">
              <img :src="arrowNext" alt="Next" class="w-5 h-5 dark:invert" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Calendar Content -->
    <div class="calendar-content">
      <!-- List View -->
      <div v-if="currentView === 'list'" class="bg-white dark:bg-gray-800 rounded-lg shadow">
        <div v-if="events.length === 0" class="p-4 text-center text-gray-500 dark:text-gray-400">
          No events to display
        </div>
        <div v-else class="divide-y divide-gray-200 dark:divide-gray-700">
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

      <!-- Loading Overlay (not full screen) -->
      <div v-if="loading" class="absolute inset-0 bg-white/50 dark:bg-gray-800/50 flex justify-center items-center z-50">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>

      <!-- Error Message (as a banner, not blocking content) -->
      <div v-if="error" class="bg-red-50 dark:bg-red-900 p-4 rounded-lg mb-4">
        <p class="text-red-800 dark:text-red-200">{{ error }}</p>
        <button
          @click="fetchEvents"
          class="mt-2 text-sm text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-200"
        >
          Try again
        </button>
      </div>

      <!-- Calendar Grid (always shown) -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow">
        <!-- Month View -->
        <div v-if="currentView === 'month'" class="grid grid-cols-7 gap-0 border border-gray-200 dark:border-gray-700">
          <!-- Days of week header -->
          <div
            v-for="day in weekDays"
            :key="day"
            class="p-2 text-center font-semibold border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800"
          >
            <div class="text-sm">{{ format(day, 'EEEE') }}</div>
            <div class="text-xs text-gray-600 dark:text-gray-400">{{ format(day, 'd MMMM') }}</div>
          </div>

          <!-- Calendar days -->
          <div
            v-for="day in currentMonthDays"
            :key="day.date"
            :class="[
              'min-h-[120px] p-2 border border-gray-200 dark:border-gray-700',
              day.isCurrentMonth ? 'bg-white dark:bg-gray-800' : 'bg-gray-50 dark:bg-gray-900',
              day.isToday ? 'bg-blue-50 dark:bg-blue-900/30' : '',
              'relative'
            ]"
          >
            <div class="flex justify-between">
              <span :class="[
                'text-sm',
                !day.isCurrentMonth && 'text-gray-400 dark:text-gray-600',
                day.isToday && 'font-bold'
              ]">
                {{ format(day.date, 'd') }}
              </span>
              <button
                @click="openEventModal(day.date)"
                class="text-blue-500 hover:text-blue-600 dark:text-blue-400 dark:hover:text-blue-300"
              >
                +
              </button>
            </div>
            <!-- Events list -->
            <div class="mt-1 space-y-1">
              <div
                v-for="event in getEventsForDay(day.date)"
                :key="event.id"
                @click="openEventModal(day.date, event)"
                class="text-xs p-1 rounded cursor-pointer"
                :class="getEventClass(event)"
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
            {{ format(currentDate, 'EEEE, d MMMM yyyy') }}
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
import { format, addDays, startOfWeek, endOfWeek, startOfMonth, endOfMonth, eachDayOfInterval, isSameMonth, isToday, parseISO, compareAsc, setMinutes, setHours, addMinutes, isWithinInterval, isBefore, isAfter, differenceInMinutes, addMonths, subMonths, addWeeks, subWeeks } from 'date-fns'
import EventModal from '@/components/EventModal.vue'
import arrowPrevious from '@/assets/arrow-previous.svg'
import arrowNext from '@/assets/arrow-next.svg'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'

// Initialize stores
const authStore = useAuthStore()

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

// Computed
const hasServerSettings = computed(() => {
  return authStore.serverSettings?.serverUrl
})

// Week days array for headers
const weekDays = computed(() => {
  const start = startOfWeek(currentDate.value, { weekStartsOn: 1 })
  return Array.from({ length: 7 }, (_, i) => addDays(start, i))
})

// Current period label
const currentPeriodLabel = computed(() => {
  if (currentView.value === 'month') {
    return format(currentDate.value, 'MMMM yyyy')
  } else if (currentView.value === 'week') {
    const start = startOfWeek(currentDate.value, { weekStartsOn: 1 })
    const end = endOfWeek(currentDate.value, { weekStartsOn: 1 })
    return `${format(start, 'MMM d')} - ${format(end, 'MMM d, yyyy')}`
  } else {
    return format(currentDate.value, 'EEEE, d MMMM yyyy')
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

const currentMonthDays = computed(() => {
  const start = startOfMonth(currentDate.value)
  const end = endOfMonth(currentDate.value)
  const days = eachDayOfInterval({ start, end })
  
  // Get the first day of the month
  const firstDayOfMonth = startOfMonth(currentDate.value)
  
  // Get the last day of the month
  const lastDayOfMonth = endOfMonth(currentDate.value)
  
  // Get the start of the first week
  const startDate = startOfWeek(firstDayOfMonth, { weekStartsOn: 1 })
  
  // Get the end of the last week
  const endDate = endOfWeek(lastDayOfMonth, { weekStartsOn: 1 })
  
  // Generate all days
  const allDays = eachDayOfInterval({ start: startDate, end: endDate })
  
  return allDays.map(date => ({
    date,
    isCurrentMonth: isSameMonth(date, currentDate.value),
    isToday: isToday(date)
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

const getDayEvents = (date) => {
  return getEventsForDate(date)
}

const getEventsForDate = (date) => {
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

const getEventClass = (event) => {
  return [
    `bg-${event.color || 'blue'}-100`,
    `text-${event.color || 'blue'}-800`,
    `dark:bg-${event.color || 'blue'}-800`,
    `dark:text-${event.color || 'blue'}-100`
  ]
}

function openNewEventModal(date = null) {
  selectedEvent.value = null
  selectedDate.value = date || currentDate.value
  showEventModal.value = true
}

function openEventModal(date, event = null) {
  showEventModal.value = true
  selectedDate.value = date
  selectedEvent.value = event
}

function closeEventModal() {
  showEventModal.value = false
  selectedEvent.value = null
  selectedDate.value = null
}

const fetchEvents = async () => {
  if (!hasServerSettings.value) {
    error.value = 'Server settings not configured. Please configure Baikal settings first.'
    return
  }

  loading.value = true
  error.value = null
  try {
    console.log('Fetching events with settings:', authStore.serverSettings)
    
    // Calculate date range based on current view
    let startDate, endDate
    if (currentView.value === 'month') {
      startDate = startOfMonth(currentDate.value)
      endDate = endOfMonth(currentDate.value)
    } else if (currentView.value === 'week') {
      startDate = startOfWeek(currentDate.value, { weekStartsOn: 1 })
      endDate = endOfWeek(currentDate.value, { weekStartsOn: 1 })
    } else if (currentView.value === 'day') {
      startDate = new Date(currentDate.value.setHours(0, 0, 0, 0))
      endDate = new Date(currentDate.value.setHours(23, 59, 59, 999))
    } else {
      // For list view, show events for the next 30 days
      startDate = new Date()
      endDate = addDays(startDate, 30)
    }

    const response = await axios.get('/api/calendar/events', {
      params: {
        start: startDate.toISOString(),
        end: endDate.toISOString()
      }
    })
    
    console.log('Calendar response:', response.data)
    
    if (response.data?.error) {
      error.value = response.data.error
      events.value = []
      return
    }
    
    events.value = Array.isArray(response.data) ? response.data : []
    console.log('Processed events:', events.value)
  } catch (err) {
    console.error('Error fetching events:', err)
    error.value = err.response?.data?.error || 'Failed to load events'
    events.value = []
  } finally {
    loading.value = false
  }
}

const saveEvent = async (eventData) => {
  try {
    if (eventData.id) {
      await axios.put(`/api/calendar/events/${eventData.id}`, eventData)
    } else {
      await axios.post('/api/calendar/events', eventData)
    }
    await fetchEvents()
    showEventModal.value = false
    selectedEvent.value = null
  } catch (err) {
    error.value = err.response?.data?.error || 'Failed to save event'
    console.error('Error saving event:', err)
  }
}

const deleteEvent = async (eventId) => {
  try {
    await axios.delete(`/api/calendar/events/${eventId}`)
    await fetchEvents()
    showEventModal.value = false
    selectedEvent.value = null
  } catch (err) {
    error.value = err.response?.data?.error || 'Failed to delete event'
    console.error('Error deleting event:', err)
  }
}

// Watch for view/date changes to refresh events
watch([currentView, currentDate], async () => {
  if (hasServerSettings.value) {
    await fetchEvents()
  }
})

// Initialize calendar immediately
onMounted(async () => {
  // Always initialize with empty events
  events.value = []
  
  // Ensure settings are loaded
  await authStore.ensureSettings()
  
  // Only fetch events if we have server settings
  if (hasServerSettings.value) {
    await fetchEvents()
  } else {
    error.value = 'Server settings not configured. Please configure Baikal settings first.'
  }
})

// Watch for server settings changes
watch(() => authStore.serverSettings, async (newSettings) => {
  if (newSettings?.serverUrl) {
    error.value = null
    await fetchEvents()
  } else {
    error.value = 'Server settings not configured. Please configure Baikal settings first.'
  }
}, { immediate: true })

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

const hasEvents = (date) => {
  return events.value.some(event => {
    const eventDate = new Date(event.start)
    return eventDate.getDate() === date.getDate() &&
           eventDate.getMonth() === date.getMonth() &&
           eventDate.getFullYear() === date.getFullYear()
  })
}

const getEventsForDay = (date) => {
  return events.value.filter(event => {
    const eventDate = new Date(event.start)
    return eventDate.getDate() === date.getDate() &&
           eventDate.getMonth() === date.getMonth() &&
           eventDate.getFullYear() === date.getFullYear()
  })
}
</script> 