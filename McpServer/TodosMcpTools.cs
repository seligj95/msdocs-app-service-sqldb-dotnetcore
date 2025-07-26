using DotNetCoreSqlDb.Data;
using DotNetCoreSqlDb.Models;
using Microsoft.EntityFrameworkCore;
using System.ComponentModel;
using ModelContextProtocol.Server;

namespace DotNetCoreSqlDb.McpServer
{
    [McpServerToolType]
    public class TodosMcpTool
    {
        private readonly MyDatabaseContext _db;

        public TodosMcpTool(MyDatabaseContext db)
        {
            _db = db;
        }

        [McpServerTool, Description("Creates a new todo with a description and creation date.")]
        public async Task<string> CreateTodoAsync(
            [Description("Description of the todo")] string description,
            [Description("Creation date of the todo")] DateTime createdDate)
        {
            var todo = new Todo
            {
                Description = description,
                CreatedDate = createdDate
            };
            _db.Todo.Add(todo);
            await _db.SaveChangesAsync();
            return $"Todo created: {todo.Description} (Id: {todo.ID})";
        }

        [McpServerTool, Description("Reads all todos, or a single todo if an id is provided.")]
        public async Task<List<Todo>> ReadTodosAsync(
            [Description("Id of the todo to read (optional)")] string? id = null)
        {
            if (!string.IsNullOrWhiteSpace(id) && int.TryParse(id, out int todoId))
            {
                var todo = await _db.Todo.FindAsync(todoId);
                if (todo == null) return new List<Todo>();
                return new List<Todo> { todo };
            }
            var todos = await _db.Todo.OrderBy(t => t.ID).ToListAsync();
            return todos;
        }

        [McpServerTool, Description("Updates the specified todo fields by id.")]
        public async Task<string> UpdateTodoAsync(
            [Description("Id of the todo to update")] string id,
            [Description("New description (optional)")] string? description = null,
            [Description("New creation date (optional)")] DateTime? createdDate = null)
        {
            if (!int.TryParse(id, out int todoId))
                return "Invalid todo id.";
            var todo = await _db.Todo.FindAsync(todoId);
            if (todo == null) return $"Todo with Id {todoId} not found.";
            if (!string.IsNullOrWhiteSpace(description)) todo.Description = description;
            if (createdDate.HasValue) todo.CreatedDate = createdDate.Value;
            await _db.SaveChangesAsync();
            return $"Todo {todo.ID} updated.";
        }

        [McpServerTool, Description("Deletes a todo by id.")]
        public async Task<string> DeleteTodoAsync(
            [Description("Id of the todo to delete")] string id)
        {
            if (!int.TryParse(id, out int todoId))
                return "Invalid todo id.";
            var todo = await _db.Todo.FindAsync(todoId);
            if (todo == null) return $"Todo with Id {todoId} not found.";
            _db.Todo.Remove(todo);
            await _db.SaveChangesAsync();
            return $"Todo {todo.ID} deleted.";
        }
    }
}