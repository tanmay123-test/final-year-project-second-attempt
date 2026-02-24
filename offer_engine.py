"""
Sequential Offer & Timeout Engine
Phase 7: Smart job offer management with timeout handling
"""

import threading
import time
import uuid
from datetime import datetime, timedelta
from typing import Callable, Optional, Dict, List, Tuple
from dispatch_engine import JobRequest, Mechanic, JobOffer, OfferStatus, JobStatus, dispatch_engine

class OfferEngine:
    """Manages sequential job offers with timeout handling"""
    
    def __init__(self):
        self.active_offers: Dict[str, JobOffer] = {}
        self.offer_callbacks: Dict[str, Callable] = {}
        self.timeout_threads: Dict[str, threading.Thread] = {}
        
    def create_offer(self, job: JobRequest, mechanic: Mechanic, eta_minutes: int) -> JobOffer:
        """Create a job offer to a mechanic"""
        offer_id = str(uuid.uuid4())
        offer = JobOffer(
            id=offer_id,
            job_id=job.id,
            mechanic_id=mechanic.id,
            offered_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(seconds=dispatch_engine.OFFER_TIMEOUT_SECONDS),
            eta_minutes=eta_minutes
        )
        
        self.active_offers[offer_id] = offer
        
        # Start timeout timer
        self._start_timeout_timer(offer)
        
        dispatch_engine._log_job_event(
            job.id, "OFFER_CREATED", 
            f"Offer sent to mechanic {mechanic.name} (ETA: {eta_minutes} mins)"
        )
        
        return offer
    
    def _start_timeout_timer(self, offer: JobOffer):
        """Start timeout thread for offer"""
        def timeout_callback():
            time.sleep(dispatch_engine.OFFER_TIMEOUT_SECONDS)
            if offer.id in self.active_offers and offer.status == OfferStatus.OFFERED:
                self._handle_offer_timeout(offer)
        
        thread = threading.Thread(target=timeout_callback, daemon=True)
        thread.start()
        self.timeout_threads[offer.id] = thread
    
    def _handle_offer_timeout(self, offer: JobOffer):
        """Handle offer expiration"""
        if offer.status == OfferStatus.OFFERED:
            offer.status = OfferStatus.EXPIRED
            dispatch_engine._log_job_event(
                offer.job_id, "OFFER_EXPIRED",
                f"Offer to mechanic {offer.mechanic_id} expired"
            )
            
            # Trigger next offer if callback exists
            if offer.job_id in self.offer_callbacks:
                self.offer_callbacks[offer.job_id]()
    
    def accept_offer(self, offer_id: str) -> bool:
        """Mechanic accepts the offer"""
        if offer_id not in self.active_offers:
            return False
        
        offer = self.active_offers[offer_id]
        
        if offer.status != OfferStatus.OFFERED:
            return False
        
        if datetime.utcnow() > offer.expires_at:
            offer.status = OfferStatus.EXPIRED
            return False
        
        offer.status = OfferStatus.ACCEPTED
        offer.responded_at = datetime.utcnow()
        
        dispatch_engine._log_job_event(
            offer.job_id, "OFFER_ACCEPTED",
            f"Mechanic {offer.mechanic_id} accepted offer"
        )
        
        return True
    
    def reject_offer(self, offer_id: str) -> bool:
        """Mechanic rejects the offer"""
        if offer_id not in self.active_offers:
            return False
        
        offer = self.active_offers[offer_id]
        offer.status = OfferStatus.REJECTED
        offer.responded_at = datetime.utcnow()
        
        dispatch_engine._log_job_event(
            offer.job_id, "OFFER_REJECTED",
            f"Mechanic {offer.mechanic_id} rejected offer"
        )
        
        return True
    
    def set_callback(self, job_id: str, callback: Callable):
        """Set callback for when offer times out"""
        self.offer_callbacks[job_id] = callback
    
    def cleanup_offers(self, job_id: str):
        """Clean up offers for a completed job"""
        offers_to_remove = []
        for offer_id, offer in self.active_offers.items():
            if offer.job_id == job_id:
                offers_to_remove.append(offer_id)
        
        for offer_id in offers_to_remove:
            del self.active_offers[offer_id]
            if offer_id in self.offer_callbacks:
                del self.offer_callbacks[offer_id]
            if offer_id in self.timeout_threads:
                # Note: Thread will terminate naturally
                del self.timeout_threads[offer_id]

class SequentialOfferManager:
    """Manages the sequential offer process for jobs"""
    
    def __init__(self, offer_engine: OfferEngine):
        self.offer_engine = offer_engine
        self.job_offer_queues: Dict[str, List[Tuple[Mechanic, float]]] = {}
    
    def start_sequential_offers(self, job: JobRequest, ranked_mechanics: List[Tuple[Mechanic, float]]):
        """Start sequential offer process for a job"""
        self.job_offer_queues[job.id] = ranked_mechanics
        
        # Set callback for moving to next offer
        self.offer_engine.set_callback(job.id, lambda: self._offer_next_mechanic(job.id))
        
        # Start with first mechanic
        self._offer_next_mechanic(job.id)
    
    def _offer_next_mechanic(self, job_id: str):
        """Offer job to next mechanic in queue"""
        if job_id not in self.job_offer_queues:
            return
        
        mechanics_queue = self.job_offer_queues[job_id]
        
        if not mechanics_queue:
            # No more mechanics to offer
            dispatch_engine._log_job_event(job_id, "NO_MORE_MECHANICS", "All mechanics declined/timeout")
            self._handle_no_mechanics_found(job_id)
            return
        
        # Get next mechanic
        mechanic, score = mechanics_queue.pop(0)
        
        # Calculate ETA
        job = dispatch_engine.active_jobs.get(job_id)
        if not job:
            return
        
        distance, eta = dispatch_engine.calculate_distance_and_eta(
            mechanic.current_location, job.location
        )
        
        # Create offer
        offer = self.offer_engine.create_offer(job, mechanic, eta)
        
        # Update job status
        job.status = JobStatus.OFFERED
        
        dispatch_engine._log_job_event(
            job_id, "OFFER_SENT",
            f"Offer sent to {mechanic.name} (Score: {score:.2f}, ETA: {eta} mins)"
        )
    
    def _handle_no_mechanics_found(self, job_id: str):
        """Handle case when no mechanics accept the job"""
        job = dispatch_engine.active_jobs.get(job_id)
        if job:
            job.status = JobStatus.NO_MECHANIC_FOUND
            
            # TODO: Implement radius expansion logic
            dispatch_engine._log_job_event(
                job_id, "NO_MECHANIC_FOUND",
                "No mechanics available. Consider expanding search radius."
            )
    
    def handle_mechanic_response(self, offer_id: str, accepted: bool) -> bool:
        """Handle mechanic's response to offer"""
        if accepted:
            success = self.offer_engine.accept_offer(offer_id)
            if success:
                offer = self.offer_engine.active_offers[offer_id]
                job = dispatch_engine.active_jobs.get(offer.job_id)
                if job:
                    job.status = JobStatus.ACCEPTED
                    job.mechanic_id = offer.mechanic_id
                    job.accepted_at = datetime.utcnow()
                    
                    # Update mechanic status
                    mechanic = dispatch_engine.mechanics.get(offer.mechanic_id)
                    if mechanic:
                        mechanic.status = MechanicStatus.BUSY
                    
                    dispatch_engine._log_job_event(
                        offer.job_id, "JOB_ACCEPTED",
                        f"Job accepted by mechanic {offer.mechanic_id}"
                    )
                    
                    # Clean up other offers
                    self.offer_engine.cleanup_offers(offer.job_id)
                    
                    # Start tracking
                    self._start_job_tracking(offer.job_id, offer.mechanic_id)
                
            return success
        else:
            return self.offer_engine.reject_offer(offer_id)
    
    def _start_job_tracking(self, job_id: str, mechanic_id: int):
        """Start live tracking for accepted job"""
        job = dispatch_engine.active_jobs.get(job_id)
        mechanic = dispatch_engine.mechanics.get(mechanic_id)
        
        if job and mechanic and mechanic.current_location:
            from dispatch_engine import TrackingSession
            
            tracking_session = TrackingSession(
                id=str(uuid.uuid4()),
                job_id=job_id,
                mechanic_id=mechanic_id,
                start_location=mechanic.current_location,
                current_location=mechanic.current_location,
                started_at=datetime.utcnow(),
                last_update=datetime.utcnow(),
                eta_minutes=0
            )
            
            dispatch_engine.tracking_sessions[job_id] = tracking_session
            
            dispatch_engine._log_job_event(
                job_id, "TRACKING_STARTED",
                f"Live tracking started for mechanic {mechanic_id}"
            )

# Initialize offer engine
offer_engine = OfferEngine()
sequential_offer_manager = SequentialOfferManager(offer_engine)
