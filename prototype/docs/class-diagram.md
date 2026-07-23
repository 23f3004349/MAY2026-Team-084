classDiagram

class User {
  +int userId
  +string name
  +string email
  +string phone
  +string password
  +string role
  +string status
  +login()
  +updateProfile()
}

class Flat {
  +int flatId
  +string blockName
  +string flatNumber
  +int floorNumber
  +string status
  +updateFlatDetails()
}

class Membership {
  +int membershipId
  +int userId
  +int flatId
  +string memberType
  +date startDate
  +date endDate
  +string status
  +activateMembership()
  +deactivateMembership()
}

class Complaint {
  +int complaintId
  +int flatId
  +int raisedBy
  +string title
  +string description
  +string category
  +string priority
  +string status
  +date createdAt
  +raiseComplaint()
  +updateStatus()
  +closeComplaint()
}

class ComplaintAssignment {
  +int assignmentId
  +int complaintId
  +int assignedTo
  +int assignedBy
  +date assignedDate
  +date expectedCompletionDate
  +string status
  +string remarks
  +assignWorker()
  +updateProgress()
}

class Invoice {
  +int invoiceId
  +string invoiceNumber
  +int flatId
  +int userId
  +int complaintId
  +string invoiceType
  +double amount
  +date dueDate
  +string status
  +date paidDate
  +string paymentMode
  +generateInvoice()
  +markAsPaid()
  +markAsOverdue()
}

User "1" --> "0..*" Membership : has
Flat "1" --> "0..*" Membership : contains
User "1" --> "0..*" Complaint : raises
Flat "1" --> "0..*" Complaint : has
Complaint "1" --> "0..1" ComplaintAssignment : assigned through
User "1" --> "0..*" ComplaintAssignment : worker/manager
Flat "1" --> "0..*" Invoice : receives
User "1" --> "0..*" Invoice : billed to
Complaint "0..1" --> "0..1" Invoice : may generate
