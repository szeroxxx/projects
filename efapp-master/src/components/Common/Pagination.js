import React from "react";
import Pagination from "react-bootstrap/Pagination";

const CustomPagination = ({ currentPage, totalPages, onPageChange }) => {
  const pageItems = [];
  for (let i = 1; i <= totalPages; i++) {
    if(i <= 5){
      pageItems.push(
        <Pagination.Item
          key={i}
          active={i === currentPage}
          onClick={() => onPageChange(i)}
        >
          {i}
        </Pagination.Item>
      );
    }
  }

  return (
    <Pagination>
      <Pagination.First
        disabled={currentPage === 1}
        onClick={() => onPageChange(1)}
      />
      <Pagination.Prev
        disabled={currentPage === 1}
        onClick={() => onPageChange(currentPage - 1)}
      />
      {pageItems}
      <Pagination.Next
        disabled={currentPage === totalPages}
        onClick={() => onPageChange(currentPage + 1)}
      />
      <Pagination.Last
        disabled={currentPage === totalPages}
        onClick={() => onPageChange(totalPages)}
      />
    </Pagination>
  );
};

export default CustomPagination;
