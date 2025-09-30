get_max <- function(values) {
  return(max(values, na.rm = TRUE))
}

process_list <- function(items, transform = NULL) {
  if (!is.null(transform)) {
    items <- lapply(items, transform)
  }
  return(unlist(items))
}