"""
Automation Engine for London Property Search Analyzer
Handles automated tasks, scheduling, and background processing
"""

import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
import logging


class AutomationEngine:
    """
    Handles automated property search tasks, email scheduling, 
    and background data processing
    """

    def __init__(self):
        self.scheduled_tasks = []
        self.running_tasks = {}
        self.task_history = []

        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def schedule_search(self, search_params: Dict, frequency: str = 'daily', 
                       callback: Optional[Callable] = None) -> str:
        """
        Schedule automated property searches

        Args:
            search_params: Search parameters dict
            frequency: 'daily', 'weekly', or 'monthly'
            callback: Function to call with results

        Returns:
            Task ID string
        """
        task_id = f"search_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        task = {
            'id': task_id,
            'type': 'search',
            'params': search_params,
            'frequency': frequency,
            'callback': callback,
            'next_run': self._calculate_next_run(frequency),
            'status': 'scheduled',
            'created': datetime.now()
        }

        self.scheduled_tasks.append(task)
        self.logger.info(f"Scheduled search task {task_id} with frequency {frequency}")

        return task_id

    def schedule_email_report(self, email: str, search_params: Dict, 
                            frequency: str = 'daily', time_slot: str = '09:00') -> str:
        """
        Schedule automated email reports

        Args:
            email: Recipient email address
            search_params: Search parameters for the report
            frequency: Report frequency
            time_slot: Time to send (HH:MM format)

        Returns:
            Task ID string
        """
        task_id = f"email_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        task = {
            'id': task_id,
            'type': 'email_report',
            'email': email,
            'search_params': search_params,
            'frequency': frequency,
            'time_slot': time_slot,
            'next_run': self._calculate_next_run(frequency, time_slot),
            'status': 'scheduled',
            'created': datetime.now()
        }

        self.scheduled_tasks.append(task)
        self.logger.info(f"Scheduled email report {task_id} to {email}")

        return task_id

    def start_automation_engine(self):
        """Start the automation engine in a background thread"""
        if hasattr(self, '_engine_thread') and self._engine_thread.is_alive():
            self.logger.warning("Automation engine already running")
            return

        self._engine_running = True
        self._engine_thread = threading.Thread(target=self._engine_loop, daemon=True)
        self._engine_thread.start()

        self.logger.info("Automation engine started")

    def stop_automation_engine(self):
        """Stop the automation engine"""
        self._engine_running = False
        if hasattr(self, '_engine_thread'):
            self._engine_thread.join(timeout=5)

        self.logger.info("Automation engine stopped")

    def _engine_loop(self):
        """Main automation engine loop"""
        while self._engine_running:
            try:
                current_time = datetime.now()

                # Check for tasks ready to run
                for task in self.scheduled_tasks:
                    if (task['status'] == 'scheduled' and 
                        task['next_run'] <= current_time):

                        self._execute_task(task)

                # Sleep for 60 seconds before next check
                time.sleep(60)

            except Exception as e:
                self.logger.error(f"Error in automation engine: {e}")
                time.sleep(60)

    def _execute_task(self, task: Dict):
        """Execute a scheduled task"""
        task_id = task['id']
        task['status'] = 'running'
        task['started'] = datetime.now()

        try:
            if task['type'] == 'search':
                self._execute_search_task(task)
            elif task['type'] == 'email_report':
                self._execute_email_task(task)

            task['status'] = 'completed'
            task['completed'] = datetime.now()

            # Schedule next run
            task['next_run'] = self._calculate_next_run(
                task['frequency'], 
                task.get('time_slot', '09:00')
            )
            task['status'] = 'scheduled'

        except Exception as e:
            task['status'] = 'failed'
            task['error'] = str(e)
            self.logger.error(f"Task {task_id} failed: {e}")

        # Add to history
        self.task_history.append({
            'task_id': task_id,
            'type': task['type'],
            'status': task['status'],
            'executed_at': task.get('started'),
            'completed_at': task.get('completed'),
            'error': task.get('error')
        })

    def _execute_search_task(self, task: Dict):
        """Execute an automated search task"""
        # This would integrate with the API simulator
        from .api_simulator import APISimulator

        api_simulator = APISimulator()
        results = api_simulator.search_properties(task['params'])

        # Call callback if provided
        if task['callback'] and callable(task['callback']):
            task['callback'](results)

        # Store results
        task['last_results'] = results
        task['result_count'] = len(results) if results else 0

        self.logger.info(f"Search task {task['id']} found {task['result_count']} properties")

    def _execute_email_task(self, task: Dict):
        """Execute an email report task"""
        # This would integrate with email service in production
        self.logger.info(f"Sending email report to {task['email']}")

        # Simulate email sending
        time.sleep(2)

        # In production, this would:
        # 1. Generate the search results
        # 2. Create formatted report
        # 3. Send via email service (SendGrid, AWS SES, etc.)

        task['emails_sent'] = task.get('emails_sent', 0) + 1

    def _calculate_next_run(self, frequency: str, time_slot: str = '09:00') -> datetime:
        """Calculate next run time based on frequency"""
        now = datetime.now()
        hour, minute = map(int, time_slot.split(':'))

        if frequency == 'daily':
            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(days=1)

        elif frequency == 'weekly':
            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            days_ahead = 7 - now.weekday()  # Next Monday
            if days_ahead <= 0:  # Target day already passed this week
                days_ahead += 7
            next_run += timedelta(days=days_ahead)

        elif frequency == 'monthly':
            next_run = now.replace(day=1, hour=hour, minute=minute, second=0, microsecond=0)
            # Next month
            if next_run.month == 12:
                next_run = next_run.replace(year=next_run.year + 1, month=1)
            else:
                next_run = next_run.replace(month=next_run.month + 1)

        else:
            raise ValueError(f"Invalid frequency: {frequency}")

        return next_run

    def get_scheduled_tasks(self) -> List[Dict]:
        """Get all scheduled tasks"""
        return self.scheduled_tasks.copy()

    def get_task_history(self) -> List[Dict]:
        """Get task execution history"""
        return self.task_history.copy()

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a scheduled task"""
        for i, task in enumerate(self.scheduled_tasks):
            if task['id'] == task_id:
                if task['status'] == 'running':
                    self.logger.warning(f"Cannot cancel running task {task_id}")
                    return False

                self.scheduled_tasks.pop(i)
                self.logger.info(f"Cancelled task {task_id}")
                return True

        self.logger.warning(f"Task {task_id} not found")
        return False

    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """Get status of a specific task"""
        for task in self.scheduled_tasks:
            if task['id'] == task_id:
                return {
                    'id': task['id'],
                    'type': task['type'],
                    'status': task['status'],
                    'next_run': task['next_run'],
                    'created': task['created'],
                    'result_count': task.get('result_count'),
                    'emails_sent': task.get('emails_sent')
                }

        return None

    def update_task_frequency(self, task_id: str, new_frequency: str) -> bool:
        """Update the frequency of a scheduled task"""
        for task in self.scheduled_tasks:
            if task['id'] == task_id:
                task['frequency'] = new_frequency
                task['next_run'] = self._calculate_next_run(
                    new_frequency, 
                    task.get('time_slot', '09:00')
                )

                self.logger.info(f"Updated task {task_id} frequency to {new_frequency}")
                return True

        return False

    def get_automation_stats(self) -> Dict:
        """Get automation engine statistics"""
        total_tasks = len(self.scheduled_tasks)
        completed_tasks = len([h for h in self.task_history if h['status'] == 'completed'])
        failed_tasks = len([h for h in self.task_history if h['status'] == 'failed'])

        return {
            'total_scheduled_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'failed_tasks': failed_tasks,
            'success_rate': (completed_tasks / max(completed_tasks + failed_tasks, 1)) * 100,
            'engine_running': getattr(self, '_engine_running', False)
        }


# Example usage functions for demonstration
def create_sample_automation():
    """Create sample automation tasks for demonstration"""
    engine = AutomationEngine()

    # Sample search parameters
    search_params = {
        'property_type': 'Flat',
        'min_price': 300000,
        'max_price': 600000,
        'min_bedrooms': 2,
        'max_bedrooms': 3,
        'borough': 'Camden'
    }

    # Schedule daily search
    search_task_id = engine.schedule_search(search_params, 'daily')

    # Schedule weekly email report
    email_task_id = engine.schedule_email_report(
        'user@example.com', 
        search_params, 
        'weekly', 
        '09:00'
    )

    return engine, search_task_id, email_task_id
